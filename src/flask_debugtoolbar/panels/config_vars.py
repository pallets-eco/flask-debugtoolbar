from __future__ import annotations

from flask import current_app

from . import DebugPanel


class ConfigVarsDebugPanel(DebugPanel):
    """A panel to display all variables from Flask configuration."""

    name = "ConfigVars"
    has_content = True

    def nav_title(self) -> str:
        return "Config"

    def title(self) -> str:
        return "Config"

    def url(self) -> str:
        return ""

    def content(self) -> str:
        context = self.context.copy()
        context.update(
            {
                "config": current_app.config,
            }
        )
        return self.render("panels/config_vars.html", context)
