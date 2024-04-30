from __future__ import annotations

from flask import Flask
from flask.testing import FlaskClient


def load_app(name: str) -> FlaskClient:
    app: Flask = __import__(name).app
    app.config["TESTING"] = True
    return app.test_client()


def test_basic_app() -> None:
    app = load_app("basic_app")
    index = app.get("/")
    assert index.status_code == 200
    assert b'<div id="flDebug"' in index.data
