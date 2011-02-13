try:
    from flaskext.sqlalchemy import get_debug_queries
except ImportError:
    get_debug_queries = None


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
            data.append({
                'duration': query.duration,
                'sql': self._format_sql(query.statement, query.parameters),
                'context_long': query.context,
                'context': format_fname(query.context)
            })
        return self.render('panels/sqlalchemy.html', { 'queries': data})


