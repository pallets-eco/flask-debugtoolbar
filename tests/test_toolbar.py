from __future__ import annotations

import typing as t
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from flask import Flask
from flask import Response
from flask.testing import FlaskClient

from flask_debugtoolbar import DebugToolbarExtension


def load_app(name: str) -> FlaskClient:
    app: Flask = __import__(name).app
    app.config["TESTING"] = True
    return app.test_client()


def test_basic_app() -> None:
    app = load_app("basic_app")
    index = app.get("/")
    assert index.status_code == 200
    assert b'<div id="flDebug"' in index.data


def app_with_config(
    app_config: dict[str, t.Any], toolbar_config: dict[str, t.Any]
) -> Flask:
    app = Flask(__name__, **app_config)
    app.config["DEBUG"] = True
    app.config["SECRET_KEY"] = "abc123"

    for key, value in toolbar_config.items():
        app.config[key] = value

    DebugToolbarExtension(app)

    return app


def test_toolbar_is_host_matching_but_flask_is_not() -> None:
    with pytest.raises(ValueError) as e:
        app_with_config(
            app_config=dict(host_matching=False),
            toolbar_config=dict(
                DEBUG_TB_ENABLED=True, DEBUG_TB_ROUTES_HOST="myapp.com"
            ),
        )

    assert str(e.value) == (
        "`DEBUG_TB_ROUTES_HOST` should only be set if your Flask app is "
        "using `host_matching`."
    )


def test_flask_is_host_matching_but_toolbar_is_not() -> None:
    with pytest.warns(UserWarning) as record:
        app_with_config(
            app_config=dict(host_matching=True, static_host="static.com"),
            toolbar_config=dict(DEBUG_TB_ENABLED=True),
        )

    assert isinstance(record[0].message, UserWarning)
    assert record[0].message.args[0] == (
        "Flask-DebugToolbar requires DEBUG_TB_ROUTES_HOST to be set if Flask "
        "is running in `host_matching` mode. Static assets for the toolbar "
        "will not be served correctly unless this is set."
    )


def test_toolbar_host_variables_rejected() -> None:
    with pytest.raises(ValueError) as e:
        app_with_config(
            app_config=dict(host_matching=True, static_host="static.com"),
            toolbar_config=dict(
                DEBUG_TB_ENABLED=True, DEBUG_TB_ROUTES_HOST="<host>.com"
            ),
        )

    assert str(e.value) == (
        "`DEBUG_TB_ROUTES_HOST` must either be a host name with no "
        "variables, to serve all Flask-DebugToolbar assets from a single "
        "host, or `*` to match the current request's host."
    )


def test_toolbar_in_host_mode_injects_toolbar_html() -> None:
    app = app_with_config(
        app_config=dict(host_matching=True, static_host="static.com"),
        toolbar_config=dict(DEBUG_TB_ENABLED=True, DEBUG_TB_ROUTES_HOST="myapp.com"),
    )

    @app.route("/", host="myapp.com")
    def index() -> str:
        return "<html><head></head><body>OK</body></html>"

    with app.test_client() as client:
        with app.app_context():
            response = client.get("/", headers={"Host": "myapp.com"})
            assert '<div id="flDebug" ' in response.text


@pytest.mark.parametrize(
    "tb_routes_host, request_host, expected_static_path",
    (
        ("myapp.com", "myapp.com", "/_debug_toolbar/static/"),
        ("toolbar.com", "myapp.com", "http://toolbar.com/_debug_toolbar/static/"),
        ("*", "myapp.com", "/_debug_toolbar/static/"),
    ),
)
def test_toolbar_injects_expected_static_path_for_host(
    tb_routes_host: str, request_host: str, expected_static_path: str
) -> None:
    app = app_with_config(
        app_config=dict(host_matching=True, static_host="static.com"),
        toolbar_config=dict(DEBUG_TB_ENABLED=True, DEBUG_TB_ROUTES_HOST=tb_routes_host),
    )

    @app.route("/", host=request_host)
    def index() -> str:
        return "<html><head></head><body>OK</body></html>"

    with app.test_client() as client:
        with app.app_context():
            response = client.get("/", headers={"Host": request_host})

            assert (
                """<script type="text/javascript">"""
                f"""var DEBUG_TOOLBAR_STATIC_PATH = '{expected_static_path}'"""
                """</script>"""
            ) in response.text


@patch(
    "flask.helpers.werkzeug.utils.send_from_directory",
    return_value=Response(b"some-file", mimetype="text/css", status=200),
)
@pytest.mark.parametrize(
    "tb_routes_host, request_host, expected_status_code",
    (
        ("toolbar.com", "toolbar.com", 200),
        ("toolbar.com", "myapp.com", 404),
        ("toolbar.com", "static.com", 404),
        ("*", "toolbar.com", 200),
        ("*", "myapp.com", 200),
        ("*", "static.com", 200),
    ),
)
def test_toolbar_serves_assets_based_on_host_configuration(
    mock_send_from_directory: MagicMock,
    tb_routes_host: str,
    request_host: str,
    expected_status_code: int,
) -> None:
    app = app_with_config(
        app_config=dict(host_matching=True, static_host="static.com"),
        toolbar_config=dict(DEBUG_TB_ENABLED=True, DEBUG_TB_ROUTES_HOST=tb_routes_host),
    )

    with app.test_client() as client:
        with app.app_context():
            response = client.get(
                "/_debug_toolbar/static/js/toolbar.js", headers={"Host": request_host}
            )
            assert response.status_code == expected_status_code
