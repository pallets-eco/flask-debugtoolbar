from __future__ import annotations

import typing as t

import itsdangerous
from flask import abort
from flask import current_app
from flask import g
from flask import request

from .. import module
from ..utils import format_fname
from ..utils import format_sql
from . import DebugPanel

try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    sqlalchemy_available: bool = False
    get_recorded_queries = SQLAlchemy = None  # type: ignore[misc, assignment]
    debug_enables_record_queries: bool = False
else:
    try:
        from flask_sqlalchemy.record_queries import (  # type: ignore[assignment]
            get_recorded_queries,
        )

        debug_enables_record_queries = False
    except ImportError:
        # For flask_sqlalchemy < 3.0.0
        from flask_sqlalchemy import (  # type: ignore[no-redef]
            get_debug_queries as get_recorded_queries,
        )

        # flask_sqlalchemy < 3.0.0 automatically enabled
        # SQLALCHEMY_RECORD_QUERIES in debug or test mode
        debug_enables_record_queries = True
        location_property: str = "context"
    else:
        location_property = "location"

    sqlalchemy_available = True


def query_signer() -> itsdangerous.URLSafeSerializer:
    return itsdangerous.URLSafeSerializer(
        current_app.config["SECRET_KEY"], salt="fdt-sql-query"
    )


def is_select(statement: str | bytes) -> bool:
    statement = statement.lower().strip()

    if isinstance(statement, bytes):
        return statement.startswith(b"select")

    return statement.startswith("select")  # pyright: ignore


def dump_query(statement: str, params: t.Any) -> str | None:
    if not params or not is_select(statement):
        return None

    try:
        return query_signer().dumps([statement, params])
    except TypeError:
        return None


def load_query(data: str) -> tuple[str, t.Any]:
    try:
        statement, params = query_signer().loads(data)
    except (itsdangerous.BadSignature, TypeError):
        abort(406)

    # Make sure it is a select statement
    if not is_select(statement):
        abort(406)

    return statement, params


def extension_used() -> bool:
    return "sqlalchemy" in current_app.extensions


def recording_enabled() -> bool:
    return (
        debug_enables_record_queries and current_app.debug
    ) or current_app.config.get("SQLALCHEMY_RECORD_QUERIES", False)


def is_available() -> bool:
    return sqlalchemy_available and extension_used() and recording_enabled()


def get_queries() -> list[t.Any]:
    if get_recorded_queries:
        return get_recorded_queries()
    else:
        return []


class SQLAlchemyDebugPanel(DebugPanel):
    """Panel that displays the time a response took in milliseconds."""

    name = "SQLAlchemy"

    @property
    def has_content(self) -> bool:  # type: ignore[override]
        return bool(get_queries()) or not is_available()

    def nav_title(self) -> str:
        return "SQLAlchemy"

    def nav_subtitle(self) -> str:
        count = len(get_queries())

        if not count and not is_available():
            return "Unavailable"

        plural = "query" if count == 1 else "queries"
        return f"{count} {plural}"

    def title(self) -> str:
        return "SQLAlchemy queries"

    def url(self) -> str:
        return ""

    def content(self) -> str:
        queries = get_queries()

        if not queries and not is_available():
            return self.render(
                "panels/sqlalchemy_error.html",
                {
                    "sqlalchemy_available": sqlalchemy_available,
                    "extension_used": extension_used(),
                    "recording_enabled": recording_enabled(),
                },
            )

        data = []

        for query in queries:
            data.append(
                {
                    "duration": query.duration,
                    "sql": format_sql(query.statement, query.parameters),
                    "signed_query": dump_query(query.statement, query.parameters),
                    "location_long": getattr(query, location_property),
                    "location": format_fname(getattr(query, location_property)),
                }
            )

        return self.render("panels/sqlalchemy.html", {"queries": data})


# Panel views


@module.route("/sqlalchemy/sql_select", methods=["GET", "POST"])
@module.route(
    "/sqlalchemy/sql_explain", methods=["GET", "POST"], defaults=dict(explain=True)
)
def sql_select(explain: bool = False) -> str:
    statement, params = load_query(request.args["query"])
    engine = current_app.extensions["sqlalchemy"].engine

    if explain:
        if engine.driver == "pysqlite":
            statement = f"EXPLAIN QUERY PLAN\n{statement}"
        else:
            statement = f"EXPLAIN\n{statement}"

    result = engine.execute(statement, params)
    return g.debug_toolbar.render(  # type: ignore[no-any-return]
        "panels/sqlalchemy_select.html",
        {
            "result": result.fetchall(),
            "headers": result.keys(),
            "sql": format_sql(statement, params),
            "duration": float(request.args["duration"]),
        },
    )
