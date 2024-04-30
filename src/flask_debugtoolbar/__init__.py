from __future__ import annotations

import collections.abc as c
import importlib.metadata
import os
import typing as t
import urllib.parse
import warnings
from contextvars import ContextVar

from flask import Blueprint
from flask import current_app
from flask import Flask
from flask import g
from flask import request
from flask import send_from_directory
from flask import url_for
from flask.globals import request_ctx
from jinja2 import Environment
from jinja2 import PackageLoader
from werkzeug import Request
from werkzeug import Response
from werkzeug.routing import Rule

from .toolbar import DebugToolbar
from .utils import decode_text
from .utils import gzip_compress
from .utils import gzip_decompress

__version__ = importlib.metadata.version("flask-debugtoolbar")
_jinja_version = importlib.metadata.version("jinja2")

module: Blueprint = Blueprint("debugtoolbar", __name__)


def replace_insensitive(string: str, target: str, replacement: str) -> str:
    """Similar to string.replace() but is case insensitive
    Code borrowed from:
    http://forums.devshed.com/python-programming-11/case-insensitive-string-replace-490921.html
    """
    no_case = string.lower()
    index = no_case.rfind(target.lower())

    if index >= 0:
        return string[:index] + replacement + string[index + len(target) :]
    else:  # no results so return the original string
        return string


def _printable(value: object) -> str:
    try:
        return decode_text(repr(value))
    except Exception as e:
        return f"<repr({object.__repr__(value)}) raised {type(e).__name__}: {e}>"


class DebugToolbarExtension:
    _static_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), "static"))

    _toolbar_codes = [200, 201, 400, 401, 403, 404, 405, 500, 501, 502, 503, 504]
    _redirect_codes = [301, 302, 303, 304]

    def __init__(self, app: Flask | None = None) -> None:
        self.app = app
        # Support threads running  `flask.copy_current_request_context` without
        # poping toolbar during `teardown_request`
        self.debug_toolbars_var: ContextVar[dict[Request, DebugToolbar]] = ContextVar(
            "debug_toolbars"
        )
        jinja_extensions = ["jinja2.ext.i18n"]

        if _jinja_version[0] == "2":
            jinja_extensions.append("jinja2.ext.with_")

        # Configure jinja for the internal templates and add url rules
        # for static data
        self.jinja_env: Environment = Environment(
            autoescape=True,
            extensions=jinja_extensions,
            loader=PackageLoader(__name__, "templates"),
        )
        self.jinja_env.filters["urlencode"] = urllib.parse.quote_plus
        self.jinja_env.filters["printable"] = _printable
        self.jinja_env.globals["url_for"] = url_for

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        for k, v in self._default_config(app).items():
            app.config.setdefault(k, v)

        if not app.config["DEBUG_TB_ENABLED"]:
            return

        if not app.config.get("SECRET_KEY"):
            raise RuntimeError(
                "The Flask-DebugToolbar requires the 'SECRET_KEY' config "
                "var to be set"
            )

        DebugToolbar.load_panels(app)

        app.before_request(self.process_request)
        app.after_request(self.process_response)
        app.teardown_request(self.teardown_request)

        # Monkey-patch the Flask.dispatch_request method
        app.dispatch_request = self.dispatch_request  # type: ignore[method-assign]

        app.add_url_rule(
            "/_debug_toolbar/static/<path:filename>",
            "_debug_toolbar.static",
            self.send_static_file,
        )

        app.register_blueprint(module, url_prefix="/_debug_toolbar/views")

    def _default_config(self, app: Flask) -> dict[str, t.Any]:
        return {
            "DEBUG_TB_ENABLED": app.debug,
            "DEBUG_TB_HOSTS": (),
            "DEBUG_TB_INTERCEPT_REDIRECTS": True,
            "DEBUG_TB_PANELS": (
                "flask_debugtoolbar.panels.versions.VersionDebugPanel",
                "flask_debugtoolbar.panels.timer.TimerDebugPanel",
                "flask_debugtoolbar.panels.headers.HeaderDebugPanel",
                "flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel",
                "flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel",
                "flask_debugtoolbar.panels.template.TemplateDebugPanel",
                "flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel",
                "flask_debugtoolbar.panels.logger.LoggingPanel",
                "flask_debugtoolbar.panels.route_list.RouteListDebugPanel",
                "flask_debugtoolbar.panels.profiler.ProfilerDebugPanel",
                "flask_debugtoolbar.panels.g.GDebugPanel",
            ),
            "SQLALCHEMY_RECORD_QUERIES": app.debug,
        }

    def dispatch_request(self) -> t.Any:
        """Modified version of ``Flask.dispatch_request`` to call
        :meth:`process_view`.
        """
        # self references this extension, use current_app to call app methods.
        app = current_app._get_current_object()  # type: ignore[attr-defined]
        req = request_ctx.request

        if req.routing_exception is not None:
            app.raise_routing_exception(req)

        rule: Rule = req.url_rule  # type: ignore[assignment]

        if (
            getattr(rule, "provide_automatic_options", False)
            and req.method == "OPTIONS"
        ):
            return app.make_default_options_response()

        view_func = app.view_functions[rule.endpoint]
        view_args: dict[str, t.Any] = req.view_args  # type: ignore[assignment]
        # allow each toolbar to process the view and args
        view_func = self.process_view(app, view_func, view_args)
        return view_func(**view_args)

    def _show_toolbar(self) -> bool:
        """Return a boolean to indicate if we need to show the toolbar."""
        if request.blueprint == "debugtoolbar":
            return False

        hosts = current_app.config["DEBUG_TB_HOSTS"]

        if hosts and request.remote_addr not in hosts:
            return False

        return True

    def send_static_file(self, filename: str) -> Response:
        """Send a static file from the flask-debugtoolbar static directory."""
        return send_from_directory(self._static_dir, filename)

    def process_request(self) -> None:
        g.debug_toolbar = self

        if not self._show_toolbar():
            return

        real_request = request._get_current_object()  # type: ignore[attr-defined]
        self.debug_toolbars_var.set({})
        self.debug_toolbars_var.get()[real_request] = DebugToolbar(
            real_request, self.jinja_env
        )

        for panel in self.debug_toolbars_var.get()[real_request].panels:
            panel.process_request(real_request)

    def process_view(
        self,
        app: Flask,
        view_func: c.Callable[..., t.Any],
        view_kwargs: dict[str, t.Any],
    ) -> c.Callable[..., t.Any]:
        """This method is called just before the flask view is called.
        This is done by the dispatch_request method.
        """
        real_request = request._get_current_object()  # type: ignore[attr-defined]

        try:
            toolbar = self.debug_toolbars_var.get({})[real_request]
        except KeyError:
            return view_func

        for panel in toolbar.panels:
            new_view = panel.process_view(real_request, view_func, view_kwargs)

            if new_view:
                view_func = new_view

        return view_func

    def process_response(self, response: Response) -> Response:
        real_request = request._get_current_object()  # type: ignore[attr-defined]

        if real_request not in self.debug_toolbars_var.get({}):
            return response

        # Intercept http redirect codes and display an html page with a
        # link to the target.
        if current_app.config["DEBUG_TB_INTERCEPT_REDIRECTS"]:
            if response.status_code in self._redirect_codes:
                redirect_to = response.location
                redirect_code = response.status_code

                if redirect_to:
                    content = self.render(
                        "redirect.html",
                        {"redirect_to": redirect_to, "redirect_code": redirect_code},
                    )
                    response.content_length = len(content)
                    del response.location
                    response.response = [content]
                    response.status_code = 200

        # If the http response code is an allowed code then we process to add the
        # toolbar to the returned html response.
        if not (
            response.status_code in self._toolbar_codes
            and response.is_sequence
            and response.headers["content-type"].startswith("text/html")
        ):
            return response

        content_encoding = response.headers.get("Content-Encoding")

        if content_encoding and "gzip" in content_encoding:
            response_html = gzip_decompress(response.data).decode()
        else:
            response_html = response.get_data(as_text=True)

        no_case = response_html.lower()
        body_end = no_case.rfind("</body>")

        if body_end >= 0:
            before = response_html[:body_end]
            after = response_html[body_end:]
        elif no_case.startswith("<!doctype html>"):
            before = response_html
            after = ""
        else:
            warnings.warn(
                "Could not insert debug toolbar." " </body> tag not found in response.",
                stacklevel=1,
            )
            return response

        toolbar = self.debug_toolbars_var.get()[real_request]

        for panel in toolbar.panels:
            panel.process_response(real_request, response)

        toolbar_html = toolbar.render_toolbar()

        content = "".join((before, toolbar_html, after))
        content_bytes = content.encode("utf-8")

        if content_encoding and "gzip" in content_encoding:
            content_bytes = gzip_compress(content_bytes)

        response.response = [content_bytes]
        response.content_length = len(content_bytes)

        return response

    def teardown_request(self, exc: BaseException | None) -> None:
        # debug_toolbars_var won't be set under `flask.copy_current_request_context`
        real_request = request._get_current_object()  # type: ignore[attr-defined]
        self.debug_toolbars_var.get({}).pop(real_request, None)

    def render(self, template_name: str, context: dict[str, t.Any]) -> str:
        template = self.jinja_env.get_template(template_name)
        return template.render(**context)
