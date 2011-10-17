import hashlib

import simplejson

try:
    from flaskext.sqlalchemy import get_debug_queries
except ImportError:
    get_debug_queries = None


from flask import request, current_app, abort, json
from flask_debugtoolbar import module
from flask_debugtoolbar.panels import DebugPanel
from flask_debugtoolbar.utils import format_fname, format_sql
from flaskext.sqlalchemy import SQLAlchemy


_ = lambda x: x

class SQLAlchemyDebugPanel(DebugPanel):
    """
    Panel that displays the time a response took in milliseconds.
    """
    name = 'SQLAlchemy'


    @property
    def has_content(self):
        return True if get_debug_queries and get_debug_queries() else False

    def process_request(self, request):
        pass

    def process_response(self, request, response):
        pass

    def nav_title(self):
        return _('SQLAlchemy')

    def nav_subtitle(self):
        if get_debug_queries:
            count = len(get_debug_queries())
            return "%d %s" % (count, "query" if count == 1 else "queries")

    def title(self):
        return _('SQLAlchemy queries')

    def url(self):
        return ''

    def content(self):
        queries = get_debug_queries()
        data = []
        for query in queries:
            is_select = query.statement.strip().lower().startswith('select')
            _params = ''
            try:
                _params = json.dumps(query.parameters)
            except TypeError:
                pass # object not JSON serializable


            hash = hashlib.sha1(
                current_app.config['SECRET_KEY'] +
                query.statement + _params).hexdigest()

            data.append({
                'duration': query.duration,
                'sql': format_sql(query.statement, query.parameters),
                'raw_sql': query.statement,
                'hash': hash,
                'params': _params,
                'is_select': is_select,
                'context_long': query.context,
                'context': format_fname(query.context)
            })
        return self.render('panels/sqlalchemy.html', { 'queries': data})

# Panel views

@module.route('/sqlalchemy/sql_select', methods=['GET', 'POST'])
def sql_select(render=None):
    return ''
    statement = request.args['sql']
    params = request.args['params']

    # Validate hash
    hash = hashlib.sha1(
        current_app.config['SECRET_KEY'] + statement + params).hexdigest()
    if hash != request.args['hash']:
        return abort(406)

    # Make sure it is a select statement
    if not statement.lower().strip().startswith('select'):
        return abort(406)

    params = simplejson.loads(params)

    db = SQLAlchemy(current_app)

    result = db.engine.execute(statement, params)
    return render('panels/sqlalchemy_select.html', {
        'result': result.fetchall(),
        'headers': result.keys(),
        'sql': format_sql(statement, params),
        'duration': float(request.args['duration']),
    })

@module.route('/sqlalchemy/sql_explain', methods=['GET', 'POST'])
def sql_explain(render=None):
    statement = request.args['sql']
    params = request.args['params']

    e
    # Validate hash
    hash = hashlib.sha1(
        current_app.config['SECRET_KEY'] + statement + params).hexdigest()
    if hash != request.args['hash']:
        return abort(406)

    # Make sure it is a select statement
    if not statement.lower().strip().startswith('select'):
        return abort(406)

    params = json.loads(params)

    db = SQLAlchemy(current_app)
    if db.engine.driver == 'pysqlite':
        query = 'EXPLAIN QUERY PLAN %s' % statement
    else:
        query = 'EXPLAIN %s' % statement

    result = db.engine.execute(query, params)
    return render('panels/sqlalchemy_explain.html', {
        'result': result.fetchall(),
        'headers': result.keys(),
        'sql': format_sql(statement, params),
        'duration': float(request.args['duration']),
    })
