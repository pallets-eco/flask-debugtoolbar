from collections import OrderedDict
from flask import current_app
from flask_debugtoolbar.panels import DebugPanel
_ = lambda x: x


class SettingsVarsDebugPanel(DebugPanel):
    """
    A panel to display all variables from Flask configuration
    """
    name = 'SettingsVars'
    has_content = True

    def nav_title(self):
        return _('Settings')

    def title(self):
        return _('Settings')

    def url(self):
        return ''

    def process_request(self, request):
        self.request = request
        self.settings = OrderedDict(sorted(
            current_app.config.items(), key=lambda key_value: key_value[0]))
        self.view_func = None
        self.view_args = []
        self.view_kwargs = {}

    def process_view(self, request, view_func, view_kwargs):
        self.view_func = view_func
        self.view_kwargs = view_kwargs

    def content(self):
        context = self.context.copy()
        context.update({
            'settings': self.settings,
        })

        return self.render('panels/settings_vars.html', context)
