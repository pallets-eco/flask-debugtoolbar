
try:
    from flask.ext.sqlalchemy import get_debug_queries, SQLAlchemy
except ImportError:
    sqlalchemy_available = False
    get_debug_queries = SQLAlchemy = None
else:
    sqlalchemy_available = True

from flask import request, current_app, abort, json_available, g
from flask_debugtoolbar import module
from flask_debugtoolbar.panels import DebugPanel
from flask_debugtoolbar.utils import format_fname, format_sql
import itsdangerous


_ = lambda x: x


def query_signer():
    return itsdangerous.URLSafeSerializer(current_app.config['SECRET_KEY'],
                                          salt='fdt-sql-query')


def dump_query(statement, params):
    if not params or not statement.lower().strip().startswith('select'):
        return None

    try:
        return query_signer().dumps([statement, params])
    except TypeError:
        return None


def load_query(data):
    try:
        statement, params = query_signer().loads(request.args['query'])
    except (itsdangerous.BadSignature, TypeError):
        abort(406)

    # Make sure it is a select statement
    if not statement.lower().strip().startswith('select'):
        abort(406)

    return statement, params


class SQLAlchemyDebugPanel(DebugPanel):
    """
    Panel that displays the time a response took in milliseconds.
    """
    name = 'SQLAlchemy'


    @property
    def has_content(self):
        if not json_available or not sqlalchemy_available:
            return True # will display an error message
        return bool(get_debug_queries())

    def process_request(self, request):
        pass

    def process_response(self, request, response):
        pass

    def nav_title(self):
        return _('SQLAlchemy')

    def nav_subtitle(self):
        if not json_available or not sqlalchemy_available:
            return 'Unavailable'

        if get_debug_queries:
            count = len(get_debug_queries())
            return "%d %s" % (count, "query" if count == 1 else "queries")

    def title(self):
        return _('SQLAlchemy queries')

    def url(self):
        return ''

    def content(self):
        if not json_available or not sqlalchemy_available:
            msg = ['Missing required libraries:', '<ul>']
            if not json_available:
                msg.append('<li>simplejson</li>')
            if not sqlalchemy_available:
                msg.append('<li>Flask-SQLAlchemy</li>')
            msg.append('</ul>')
            return '\n'.join(msg)

        queries = get_debug_queries()
        data = []
        for query in queries:
            data.append({
                'duration': query.duration,
                'sql': format_sql(query.statement, query.parameters),
                'signed_query': dump_query(query.statement, query.parameters),
                'context_long': query.context,
                'context': format_fname(query.context)
            })
        return self.render('panels/sqlalchemy.html', { 'queries': data})

# Panel views

@module.route('/sqlalchemy/sql_select', methods=['GET', 'POST'])
def sql_select():
    statement, params = load_query(request.args['query'])
    engine = SQLAlchemy().get_engine(current_app)

    result = engine.execute(statement, params)
    return g.debug_toolbar.render('panels/sqlalchemy_select.html', {
        'result': result.fetchall(),
        'headers': result.keys(),
        'sql': format_sql(statement, params),
        'duration': float(request.args['duration']),
    })

@module.route('/sqlalchemy/sql_explain', methods=['GET', 'POST'])
def sql_explain():
    statement, params = load_query(request.args['query'])
    engine = SQLAlchemy().get_engine(current_app)

    if engine.driver == 'pysqlite':
        query = 'EXPLAIN QUERY PLAN %s' % statement
    else:
        query = 'EXPLAIN %s' % statement

    result = engine.execute(query, params)
    return g.debug_toolbar.render('panels/sqlalchemy_explain.html', {
        'result': result.fetchall(),
        'headers': result.keys(),
        'sql': format_sql(statement, params),
        'duration': float(request.args['duration']),
    })
