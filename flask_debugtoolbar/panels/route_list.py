from flask_debugtoolbar.panels import DebugPanel
from flask import current_app

_ = lambda x: x


class RouteListDebugPanel(DebugPanel):
    """
    Panel that displays the URL routing rules.
    """
    name = 'RouteList'
    has_content = True
    routes = []

    def nav_title(self):
        return _('Route List')

    def title(self):
        return _('Route List')

    def url(self):
        return ''

    def nav_subtitle(self):
        count = len(self.routes)
        return '%s %s' % (count, 'route' if count == 1 else 'routes')

    def process_request(self, request):
        self.routes = [
            rule
            for rule in current_app.url_map.iter_rules()
            if not rule.rule.startswith('/_debug_toolbar')
        ]

    def content(self):
        return self.render('panels/route_list.html', {
            'routes': self.routes,
        })
