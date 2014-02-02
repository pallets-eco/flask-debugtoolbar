import sys

import pytest

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


@pytest.mark.skipif(sys.version_info >= (3,),
                    reason='test only applies to Python 2')
def test_printable_unicode():
    class UnicodeRepr(object):
        def __repr__(self):
            return u'\uffff'

    printable = _printable(UnicodeRepr())
    assert "raised UnicodeEncodeError: 'ascii' codec" in printable


@pytest.mark.skipif(sys.version_info >= (3,),
                    reason='test only applies to Python 2')
def test_printable_non_ascii():
    class NonAsciiRepr(object):
        def __repr__(self):
            return 'a\xffb'

    printable = u'%s' % _printable(NonAsciiRepr())
    # should replace \xff with the unicode ? character
    assert printable == u'a\ufffdb'
