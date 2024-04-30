from __future__ import annotations

import collections.abc as c
import typing as t
from urllib.parse import unquote

from flask import current_app
from flask import Flask
from flask import url_for
from jinja2 import Environment
from werkzeug import Request
from werkzeug.utils import import_string

from .panels import DebugPanel


class DebugToolbar:
    _cached_panel_classes: t.ClassVar[dict[str, type[DebugPanel] | None]] = {}

    def __init__(self, request: Request, jinja_env: Environment) -> None:
        self.jinja_env = jinja_env
        self.request = request
        self.panels: list[DebugPanel] = []
        self.template_context: dict[str, t.Any] = {
            "static_path": url_for("_debug_toolbar.static", filename="")
        }
        self.create_panels()

    def create_panels(self) -> None:
        """Populate debug panels"""
        activated_str = self.request.cookies.get("fldt_active", "")
        activated = unquote(activated_str).split(";")

        for panel_class in self._iter_panels(current_app):
            panel_instance = panel_class(
                jinja_env=self.jinja_env, context=self.template_context
            )

            if panel_instance.dom_id() in activated:
                panel_instance.is_active = True

            self.panels.append(panel_instance)

    def render_toolbar(self) -> str:
        context = self.template_context.copy()
        context.update({"panels": self.panels})
        template = self.jinja_env.get_template("base.html")
        return template.render(**context)

    @classmethod
    def load_panels(cls, app: Flask) -> None:
        for panel_class in cls._iter_panels(app):
            # Call `.init_app()` on panels
            panel_class.init_app(app)

    @classmethod
    def _iter_panels(cls, app: Flask) -> c.Iterator[type[DebugPanel]]:
        for panel_path in app.config["DEBUG_TB_PANELS"]:
            panel_class = cls._import_panel(app, panel_path)

            if panel_class is not None:
                yield panel_class

    @classmethod
    def _import_panel(cls, app: Flask, path: str) -> type[DebugPanel] | None:
        cache = cls._cached_panel_classes

        try:
            return cache[path]
        except KeyError:
            pass

        try:
            panel_class: type[DebugPanel] | None = import_string(path)
        except ImportError as e:
            app.logger.warning("Disabled %s due to ImportError: %s", path, e)
            panel_class = None

        cache[path] = panel_class
        return panel_class
