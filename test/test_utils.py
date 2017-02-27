import ntpath
import posixpath

from flask import Markup
import pytest

from flask_debugtoolbar.utils import (_relative_paths, _shortest_relative_path,
                                      format_sql, decode_text, HAVE_PYGMENTS)


@pytest.mark.parametrize('value,paths,expected,path_module', [
    # should yield relative path to the parent directory
    ('/foo/bar', ['/foo'], ['bar'], posixpath),
    ('c:\\foo\\bar', ['c:\\foo'], ['bar'], ntpath),

    # should not yield result if no path is a parent directory
    ('/foo/bar', ['/baz'], [], posixpath),
    ('c:\\foo\\bar', ['c:\\baz'], [], ntpath),

    # should only yield relative paths for parent directories
    ('/foo/bar', ['/foo', '/baz'], ['bar'], posixpath),
    ('c:\\foo\\bar', ['c:\\foo', 'c:\\baz'], ['bar'], ntpath),

    # should yield all results when multiple parents match
    ('/foo/bar/baz', ['/foo', '/foo/bar'], ['bar/baz', 'baz'], posixpath),
    ('c:\\foo\\bar\\baz', ['c:\\foo', 'c:\\foo\\bar'],
        ['bar\\baz', 'baz'], ntpath),

    # should ignore case differences on windows
    ('c:\\Foo\\bar', ['c:\\foo'], ['bar'], ntpath),

    # should preserve original case
    ('/Foo/Bar', ['/Foo'], ['Bar'], posixpath),
    ('c:\\Foo\\Bar', ['c:\\foo'], ['Bar'], ntpath),
])
def test_relative_paths(value, paths, expected, path_module):
    assert list(_relative_paths(value, paths, path_module)) == expected


@pytest.mark.parametrize('value,paths,expected,path_module', [
    # should yield relative path to the parent directory
    ('/foo/bar', ['/foo'], 'bar', posixpath),
    ('c:\\foo\\bar', ['c:\\foo'], 'bar', ntpath),

    # should return the original value if no path is a parent directory
    ('/foo/bar', ['/baz'], '/foo/bar', posixpath),
    ('c:\\foo\\bar', ['c:\\baz'], 'c:\\foo\\bar', ntpath),

    # should yield shortest result when multiple parents match
    ('/foo/bar/baz', ['/foo', '/foo/bar'], 'baz', posixpath),
    ('c:\\foo\\bar\\baz', ['c:\\foo', 'c:\\foo\\bar'], 'baz', ntpath),
])
def test_shortest_relative_path(value, paths, expected, path_module):
    assert _shortest_relative_path(value, paths, path_module) == expected


def test_decode_text_unicode():
    value = u'\uffff'
    decoded = decode_text(value)
    assert decoded == value


def test_decode_text_ascii():
    value = 'abc'
    assert decode_text(value.encode('ascii')) == value


def test_decode_text_non_ascii():
    value = b'abc \xff xyz'
    assert isinstance(value, bytes)

    decoded = decode_text(value)
    assert not isinstance(decoded, bytes)

    assert decoded.startswith('abc')
    assert decoded.endswith('xyz')


@pytest.fixture()
def no_pygments(monkeypatch):
    monkeypatch.setattr('flask_debugtoolbar.utils.HAVE_PYGMENTS', False)


def test_format_sql_no_pygments(no_pygments):
    sql = 'select 1'
    assert format_sql(sql, {}) == sql


def test_format_sql_no_pygments_non_ascii(no_pygments):
    sql = b"select '\xff'"
    formatted = format_sql(sql, {})
    assert formatted.startswith(u"select '")


def test_format_sql_no_pygments_escape_html(no_pygments):
    sql = 'select x < 1'
    formatted = format_sql(sql, {})
    assert not isinstance(formatted, Markup)
    assert Markup('%s') % formatted == 'select x &lt; 1'


@pytest.mark.skipif(not HAVE_PYGMENTS,
                    reason='test requires the "Pygments" library')
def test_format_sql_pygments():
    sql = 'select 1'
    html = format_sql(sql, {})
    assert isinstance(html, Markup)
    assert html.startswith('<div')
    assert 'select' in html
    assert '1' in html


@pytest.mark.skipif(not HAVE_PYGMENTS,
                    reason='test requires the "Pygments" library')
def test_format_sql_pygments_non_ascii():
    sql = b"select 'abc \xff xyz'"
    html = format_sql(sql, {})
    assert isinstance(html, Markup)
    assert html.startswith('<div')
    assert 'select' in html
    assert 'abc' in html
    assert 'xyz' in html
