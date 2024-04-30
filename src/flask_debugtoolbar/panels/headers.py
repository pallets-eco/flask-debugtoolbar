from __future__ import annotations

import typing as t

from werkzeug import Request

from . import DebugPanel


class HeaderDebugPanel(DebugPanel):
    """A panel to display HTTP headers."""

    name = "Header"
    has_content = True
    # List of headers we want to display
    header_filter: tuple[str, ...] = (
        "CONTENT_TYPE",
        "HTTP_ACCEPT",
        "HTTP_ACCEPT_CHARSET",
        "HTTP_ACCEPT_ENCODING",
        "HTTP_ACCEPT_LANGUAGE",
        "HTTP_CACHE_CONTROL",
        "HTTP_CONNECTION",
        "HTTP_HOST",
        "HTTP_KEEP_ALIVE",
        "HTTP_REFERER",
        "HTTP_USER_AGENT",
        "QUERY_STRING",
        "REMOTE_ADDR",
        "REMOTE_HOST",
        "REQUEST_METHOD",
        "SCRIPT_NAME",
        "SERVER_NAME",
        "SERVER_PORT",
        "SERVER_PROTOCOL",
        "SERVER_SOFTWARE",
    )

    def nav_title(self) -> str:
        return "HTTP Headers"

    def title(self) -> str:
        return "HTTP Headers"

    def url(self) -> str:
        return ""

    def process_request(self, request: Request) -> None:
        self.headers: dict[str, t.Any] = {
            k: request.environ[k] for k in self.header_filter if k in request.environ
        }

    def content(self) -> str:
        context = self.context.copy()
        context.update({"headers": self.headers})
        return self.render("panels/headers.html", context)
