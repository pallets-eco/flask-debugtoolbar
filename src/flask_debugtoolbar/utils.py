from __future__ import annotations

import collections.abc as c
import gzip
import io
import itertools
import os.path
import sys
from types import ModuleType

from flask import current_app
from markupsafe import Markup

try:
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import SqlLexer
    from pygments.styles import get_style_by_name

    PYGMENT_STYLE = get_style_by_name("colorful")
    HAVE_PYGMENTS = True
except ImportError:
    HAVE_PYGMENTS = False

try:
    import sqlparse  # pyright: ignore

    HAVE_SQLPARSE = True
except ImportError:
    HAVE_SQLPARSE = False


def format_fname(value: str) -> str:
    # If the value has a builtin prefix, return it unchanged
    if value.startswith(("{", "<")):
        return value

    value = os.path.normpath(value)

    # If the file is absolute, try normalizing it relative to the project root
    # to handle it as a project file
    if os.path.isabs(value):
        value = _shortest_relative_path(value, [current_app.root_path], os.path)

    # If the value is a relative path, it is a project file
    if not os.path.isabs(value):
        return os.path.join(".", value)

    # Otherwise, normalize other paths relative to sys.path
    return f"<{_shortest_relative_path(value, sys.path, os.path)}>"


def _shortest_relative_path(
    value: str, paths: list[str], path_module: ModuleType
) -> str:
    relpaths = _relative_paths(value, paths, path_module)
    return min(itertools.chain(relpaths, [value]), key=len)


def _relative_paths(
    value: str, paths: list[str], path_module: ModuleType
) -> c.Iterator[str]:
    for path in paths:
        try:
            relval = path_module.relpath(value, path)
        except ValueError:
            # on Windows, relpath throws a ValueError for
            # paths with different drives
            continue

        if not relval.startswith(path_module.pardir):
            yield relval


def decode_text(value: str | bytes) -> str:
    """
    Decode a text-like value for display.

    Unicode values are returned unchanged. Byte strings will be decoded
    with a text-safe replacement for unrecognized characters.
    """
    if isinstance(value, bytes):
        return value.decode("ascii", "replace")

    return value  # pyright: ignore


def format_sql(query: str | bytes, args: object) -> str:
    if HAVE_SQLPARSE:
        query = sqlparse.format(query, reindent=True, keyword_case="upper")

    if not HAVE_PYGMENTS:
        return decode_text(query)

    return Markup(
        highlight(query, SqlLexer(), HtmlFormatter(noclasses=True, style=PYGMENT_STYLE))
    )


def gzip_compress(data: bytes, compresslevel: int = 6) -> bytes:
    buff = io.BytesIO()

    with gzip.GzipFile(fileobj=buff, mode="wb", compresslevel=compresslevel) as f:
        f.write(data)

    return buff.getvalue()


def gzip_decompress(data: bytes) -> bytes:
    with gzip.GzipFile(fileobj=io.BytesIO(data), mode="rb") as f:
        return f.read()
