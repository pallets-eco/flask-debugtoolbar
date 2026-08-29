from __future__ import annotations

import time

import pytest
from flask import Flask

from flask_debugtoolbar import DebugToolbarExtension
from flask_debugtoolbar.panels.flamegraph import build_flamegraph
from flask_debugtoolbar.panels.flamegraph import FlamegraphFrame


def make_frame(name: str, lineno: int) -> FlamegraphFrame:
    return FlamegraphFrame(
        name=name,
        module="test_app",
        filename=f"/app/{name}.py",
        lineno=lineno,
    )


def test_build_flamegraph_merges_common_stacks() -> None:
    app = Flask(__name__)
    request_frame = make_frame("request", 10)
    first_leaf = make_frame("first", 20)
    second_leaf = make_frame("second", 30)

    with app.app_context():
        blocks, height = build_flamegraph(
            {
                (request_frame, first_leaf): 2,
                (request_frame, second_leaf): 1,
            }
        )

    by_name = {block.name: block for block in blocks}

    assert height == 60
    assert by_name["all samples"].samples == 3
    assert by_name[request_frame.label].samples == 3
    assert by_name[first_leaf.label].width == pytest.approx(800)
    assert by_name[second_leaf.label].width == pytest.approx(400)
    assert by_name[second_leaf.label].x == pytest.approx(800)


def test_build_flamegraph_ignores_non_positive_samples() -> None:
    app = Flask(__name__)

    with app.app_context():
        blocks, height = build_flamegraph({(make_frame("unused", 1),): 0})

    assert blocks == []
    assert height == 0


def test_flamegraph_panel_profiles_request() -> None:
    app = Flask(__name__)
    app.config.update(
        DEBUG=True,
        DEBUG_TB_FLAMEGRAPH_ENABLED=True,
        DEBUG_TB_FLAMEGRAPH_INTERVAL=0.001,
        SECRET_KEY="secret",
        TESTING=True,
    )
    DebugToolbarExtension(app)

    @app.route("/")
    def index() -> str:
        time.sleep(0.02)
        return "<html><body>Flamegraph test</body></html>"

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b'id="flDebugFlamegraphPanel"' in response.data
    assert b'class="flDebugFlamegraphChart"' in response.data
    assert b"index (test_flamegraph)" in response.data
    assert (
        b"test_flamegraph_panel_profiles_request (test_flamegraph)" not in response.data
    )
    assert b"samples over" in response.data


@pytest.mark.parametrize("interval", [0, -0.1, True, "0.1"])
def test_flamegraph_interval_must_be_a_positive_number(
    interval: object,
) -> None:
    app = Flask(__name__)
    app.config.update(
        DEBUG=True,
        DEBUG_TB_FLAMEGRAPH_INTERVAL=interval,
        SECRET_KEY="secret",
    )

    with pytest.raises(ValueError, match="DEBUG_TB_FLAMEGRAPH_INTERVAL"):
        DebugToolbarExtension(app)
