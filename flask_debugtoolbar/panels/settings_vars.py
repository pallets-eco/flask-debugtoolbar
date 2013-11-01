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

    def content(self):
        context = self.context.copy()
        context.update({
            'settings': current_app.config,
        })

        return self.render('panels/settings_vars.html', context)
