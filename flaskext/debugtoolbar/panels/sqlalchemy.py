import hashlib

try:
    from flaskext.sqlalchemy import get_debug_queries
except ImportError:
    get_debug_queries = None


import simplejson
from flask import current_app
from flaskext.debugtoolbar.panels import DebugPanel
from flaskext.debugtoolbar.utils import format_fname, format_sql

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
                _params = simplejson.dumps(query.parameters)
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


