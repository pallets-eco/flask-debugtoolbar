from __future__ import annotations

import collections.abc as c
import typing as t

from flask import session
from werkzeug import Request

from . import DebugPanel


class RequestVarsDebugPanel(DebugPanel):
    """A panel to display request variables (POST/GET, session, cookies)."""

    name = "RequestVars"
    has_content = True

    def nav_title(self) -> str:
        return "Request Vars"

    def title(self) -> str:
        return "Request Vars"

    def url(self) -> str:
        return ""

    def process_request(self, request: Request) -> None:
        self.request = request
        self.session = session
        self.view_func: c.Callable[..., t.Any] | None = None
        self.view_kwargs: dict[str, t.Any] = {}

    def process_view(
        self,
        request: Request,
        view_func: c.Callable[..., t.Any],
        view_kwargs: dict[str, t.Any],
    ) -> None:
        self.view_func = view_func
        self.view_kwargs = view_kwargs

    def content(self) -> str:
        context = self.context.copy()
        context.update(
            {
                "get": self.request.args.lists(),
                "post": self.request.form.lists(),
                "cookies": self.request.cookies.items(),
                "view_func": (
                    f"{self.view_func.__module__}.{self.view_func.__name__}"
                    if self.view_func
                    else "[unknown]"
                ),
                "view_kwargs": self.view_kwargs or {},
                "session": self.session.items(),
            }
        )

        return self.render("panels/request_vars.html", context)
