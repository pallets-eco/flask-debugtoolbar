from __future__ import annotations

import collections.abc as c
import typing as t

from flask import Flask
from jinja2 import Environment
from werkzeug import Request
from werkzeug import Response


class DebugPanel:
    """Base class for debug panels."""

    name: str

    # If content returns something, set to true in subclass
    has_content = False

    # If the client is able to activate/de-activate the panel
    user_enable = False

    # We'll maintain a local context instance so we can expose our template
    # context variables to panels which need them:
    context: dict[str, t.Any] = {}

    # Panel methods
    def __init__(
        self, jinja_env: Environment, context: dict[str, t.Any] | None = None
    ) -> None:
        if context is not None:
            self.context.update(context)

        self.jinja_env = jinja_env
        # If the client enabled the panel
        self.is_active = False

    @classmethod
    def init_app(cls, app: Flask) -> None:
        """Method that can be overridden by child classes.
        Can be used for setting up additional URL-rules/routes.

        Example::

            class UMLDiagramPanel(DebugPanel):

                @classmethod
                def init_app(cls, app):
                    app.add_url_rule(
                        '/_flask_debugtoolbar_umldiagram/<path:filename>',
                        '_flask_debugtoolbar_umldiagram.serve_generated_image',
                        cls.serve_generated_image
                    )

                @classmethod
                def serve_generated_image(cls, app):
                    return Response(...)
        """
        pass

    def render(self, template_name: str, context: dict[str, t.Any]) -> str:
        template = self.jinja_env.get_template(template_name)
        return template.render(**context)

    def dom_id(self) -> str:
        return f"flDebug{self.name.replace(' ', '')}Panel"

    def nav_title(self) -> str:
        """Title showing in toolbar"""
        raise NotImplementedError

    def nav_subtitle(self) -> str:
        """Subtitle showing until title in toolbar"""
        return ""

    def title(self) -> str:
        """Title showing in panel"""
        raise NotImplementedError

    def url(self) -> str:
        raise NotImplementedError

    def content(self) -> str:
        raise NotImplementedError

    # Standard middleware methods
    def process_request(self, request: Request) -> None:
        pass

    def process_view(
        self,
        request: Request,
        view_func: c.Callable[..., t.Any],
        view_kwargs: dict[str, t.Any],
    ) -> c.Callable[..., t.Any] | None:
        pass

    def process_response(self, request: Request, response: Response) -> None:
        pass
