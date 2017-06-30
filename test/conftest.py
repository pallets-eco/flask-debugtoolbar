import pytest

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from flask_debugtoolbar import DebugToolbarExtension


@pytest.fixture(autouse=True)
def mock_env_development(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")


@pytest.fixture
def app_no_extensions(request):
    """ Flask app only, without any extensions. """
    _app = Flask(__name__)

    app.debug = True
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "abc123"

    # make sure these are printable in the config panel
    app.config["BYTES_VALUE"] = b"\x00"
    app.config["UNICODE_VALUE"] = u"\uffff"

    # config overrides
    if "config" in request.keywords:
        for key, value in request.keywords["config"].kwargs.items():
            app.config[key] = value

    return _app


@pytest.fixture
def app(request, app_no_extensions):
    app = app_no_extensions

    toolbar = DebugToolbarExtension(app)
    db = SQLAlchemy(app)

    class Foo(db.Model):
        __tablename__ = "foo"
        id = db.Column(db.Integer, primary_key=True)

    @app.route("/")
    def index():
        db.create_all()
        Foo.query.filter_by(id=1).all()
        return render_template("basic_app.html")

    return app


@pytest.fixture
def client(request, app):
    return app.test_client()
