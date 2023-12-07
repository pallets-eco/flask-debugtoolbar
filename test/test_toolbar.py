import sys

from flask_debugtoolbar import _printable


def load_app(name):
    app = __import__(name).app
    app.config['TESTING'] = True
    return app.test_client()


def test_basic_app():
    app = load_app('basic_app')
    index = app.get('/')
    assert index.status_code == 200
    assert b'<div id="flDebug"' in index.data
