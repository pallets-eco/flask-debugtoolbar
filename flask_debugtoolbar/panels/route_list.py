from flask_debugtoolbar.panels import DebugPanel
from flask import current_app

_ = lambda x: x


class RouteListDebugPanel(DebugPanel):
    """
    Panel that displays the time a response took in milliseconds.
    """
    name = 'Route List'
    has_content = True
    routes = []

    def nav_title(self):
        return _('Route List')

    def title(self):
        return _('Route List')

    def url(self):
        return ''

    def nav_subtitle(self):

        # get the count of routes. We need to -1 to get an acurate route count
        return "%s routes" % (len(current_app.url_map._rules) - 1)

    def process_request(self, request):
        # Clear existing routes
        self.routes = []

        # iterate through the routes
        for rule in current_app.url_map.iter_rules():
            if rule.endpoint != 'static':
                self.routes.append(rule)

    def content(self):
        context = self.context.copy()
        context.update({
            'routes': self.routes,
        })

        return self.render('panels/route_list.html', context)
