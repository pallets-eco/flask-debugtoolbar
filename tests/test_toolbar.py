from __future__ import annotations

from bs4 import BeautifulSoup
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.utils import import_string


def load_app(name: str) -> FlaskClient:
    app: Flask = __import__(name).app
    app.config["TESTING"] = True
    return app.test_client()


def test_basic_app() -> None:
    app = load_app("basic_app")
    index = app.get("/")
    assert index.status_code == 200
    assert b'<div id="flDebug"' in index.data


def test_debug_switch_included_for_user_activated_panels() -> None:
    checked_panels = set()

    app = load_app("basic_app")
    index = app.get("/")

    soup = BeautifulSoup(index.text, "html.parser")

    for panel in app.application.config["DEBUG_TB_PANELS"]:
        panel_cls = import_string(panel)
        panel_id = panel_cls.dom_id()
        panel_element = soup.select_one(f"#{panel_id}")

        assert panel_element
        assert (
            bool(panel_element.select_one(".flDebugSwitch")) is panel_cls.user_activate
        ), f"Panel {panel_id} is incorrectly showing (or not showing) a debug switch"

        checked_panels.add(panel_id)

    assert len(checked_panels) == len(app.application.config["DEBUG_TB_PANELS"])
