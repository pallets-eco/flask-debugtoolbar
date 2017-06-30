import sys

import pytest

from flask_debugtoolbar import _printable, DebugToolbarExtension


def test_basic_app(app, client):
    index = client.get('/')
    assert index.status_code == 200
    assert b'<div id="flDebug"' in index.data


@pytest.mark.config(
    DEBUG_TB_ENABLED=False
)
def test_toolbar_disabled(app, client):
    index = client.get('/')
    assert index.status_code == 200
    assert b'<div id="flDebug"' not in index.data


@pytest.mark.config(
    SECRET_KEY=None
)
def test_toolbar_no_secret_key(app_no_extensions):
    with pytest.raises(RuntimeError) as exc:
        DebugToolbarExtension(app_no_extensions)
        assert all(s in str(exc) for s in ['requires', 'SECRET_KEY'])


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
