from __future__ import annotations

from flask import current_app
from werkzeug import Request
from werkzeug.routing import Rule

from . import DebugPanel


class RouteListDebugPanel(DebugPanel):
    """Panel that displays the URL routing rules."""

    name = "RouteList"
    has_content = True
    routes: list[Rule] = []

    def nav_title(self) -> str:
        return "Route List"

    def title(self) -> str:
        return "Route List"

    def url(self) -> str:
        return ""

    def nav_subtitle(self) -> str:
        count = len(self.routes)
        plural = "route" if count == 1 else "routes"
        return f"{count} {plural}"

    def process_request(self, request: Request) -> None:
        self.routes = [
            rule
            for rule in current_app.url_map.iter_rules()
            if not rule.rule.startswith("/_debug_toolbar")
        ]

    def content(self) -> str:
        return self.render(
            "panels/route_list.html",
            {
                "routes": self.routes,
            },
        )
