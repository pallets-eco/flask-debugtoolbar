from __future__ import annotations

from flask import g

from . import DebugPanel


class GDebugPanel(DebugPanel):
    """A panel to display ``flask.g`` content."""

    name = "g"
    has_content = True

    def nav_title(self) -> str:
        return "flask.g"

    def title(self) -> str:
        return "flask.g content"

    def url(self) -> str:
        return ""

    def content(self) -> str:
        context = self.context.copy()
        context.update({"g_content": g.__dict__})
        return self.render("panels/g.html", context)
