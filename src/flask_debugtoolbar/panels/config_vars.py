from flask import current_app

from . import DebugPanel


class ConfigVarsDebugPanel(DebugPanel):
    """A panel to display all variables from Flask configuration."""

    name = "ConfigVars"
    has_content = True

    def nav_title(self):
        return "Config"

    def title(self):
        return "Config"

    def url(self):
        return ""

    def content(self):
        context = self.context.copy()
        context.update(
            {
                "config": current_app.config,
            }
        )
        return self.render("panels/config_vars.html", context)
