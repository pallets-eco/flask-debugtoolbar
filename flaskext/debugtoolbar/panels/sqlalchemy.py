try:
    from flaskext.sqlalchemy import get_debug_queries
except ImportError:
    get_debug_queries = None

try:
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import SqlLexer
    from pygments.styles import get_style_by_name
    HAVE_PYGMENTS = True
except ImportError:
    HAVE_PYGMENTS = False

from flaskext.debugtoolbar.panels import DebugPanel
_ = lambda x: x

class SQLAlchemyDebugPanel(DebugPanel):
    """
    Panel that displays the time a response took in milliseconds.
    """
    name = 'SQLAlchemy'
    if HAVE_PYGMENTS:
        style = get_style_by_name('colorful')
    else:
        style = None

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
        for query in queries:
            query.sql = self._format_sql(query.statement, query.parameters)

        return self.render('panels/sqlalchemy.html', { 'queries': queries})


    def _format_sql(self, query, args):
        if not HAVE_PYGMENTS:
            return query

        return highlight(
            query,
            SqlLexer(encoding='utf-8'),
            HtmlFormatter(encoding='utf-8', noclasses=True, style=self.style))

