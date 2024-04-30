from __future__ import annotations

import collections.abc as c
import functools
import pstats
import typing as t

from flask import current_app
from jinja2 import Environment
from werkzeug import Request
from werkzeug import Response

from ..utils import format_fname
from . import DebugPanel

try:
    import cProfile as profile
except ImportError:
    import profile  # type: ignore[no-redef]


class ProfilerDebugPanel(DebugPanel):
    """Panel that displays the time a response took with cProfile output."""

    name = "Profiler"
    user_activate = True

    is_active: bool = False
    dump_filename: str | None = None
    profiler: profile.Profile
    stats: pstats.Stats | None = None
    function_calls: list[dict[str, t.Any]]

    def __init__(
        self, jinja_env: Environment, context: dict[str, t.Any] | None = None
    ) -> None:
        super().__init__(jinja_env, context=context)

        if current_app.config.get("DEBUG_TB_PROFILER_ENABLED"):
            self.is_active = True
            self.dump_filename = current_app.config.get(
                "DEBUG_TB_PROFILER_DUMP_FILENAME"
            )

    @property
    def has_content(self) -> bool:  # type: ignore[override]
        return bool(self.profiler)

    def process_request(self, request: Request) -> None:
        if not self.is_active:
            return

        self.profiler = profile.Profile()  # pyright: ignore
        self.stats = None

    def process_view(
        self,
        request: Request,
        view_func: c.Callable[..., t.Any],
        view_kwargs: dict[str, t.Any],
    ) -> c.Callable[..., t.Any] | None:
        if self.is_active:
            func = functools.partial(self.profiler.runcall, view_func)
            functools.update_wrapper(func, view_func)
            return func

        return None

    def process_response(self, request: Request, response: Response) -> None:
        if not self.is_active:
            return

        if self.profiler is not None:
            self.profiler.disable()  # pyright: ignore

            try:
                stats = pstats.Stats(self.profiler)
            except TypeError:
                self.is_active = False
                return

            function_calls: list[dict[str, t.Any]] = []

            for func in stats.sort_stats(1).fcn_list:  # type: ignore[attr-defined]
                current: dict[str, t.Any] = {}
                info = stats.stats[func]  # type: ignore[attr-defined]

                # Number of calls
                if info[0] != info[1]:
                    current["ncalls"] = f"{info[1]}/{info[0]}"
                else:
                    current["ncalls"] = info[1]

                # Total time
                current["tottime"] = info[2] * 1000

                # Quotient of total time divided by number of calls
                if info[1]:
                    current["percall"] = info[2] * 1000 / info[1]
                else:
                    current["percall"] = 0

                # Cumulative time
                current["cumtime"] = info[3] * 1000

                # Quotient of the cumulative time divided by the number of
                # primitive calls.
                if info[0]:
                    current["percall_cum"] = info[3] * 1000 / info[0]
                else:
                    current["percall_cum"] = 0

                # Filename
                filename = pstats.func_std_string(func)  # type: ignore[attr-defined]
                current["filename_long"] = filename
                current["filename"] = format_fname(filename)
                function_calls.append(current)

            self.stats = stats
            self.function_calls = function_calls

            if self.dump_filename:
                if callable(self.dump_filename):
                    filename = self.dump_filename()
                else:
                    filename = self.dump_filename

                self.profiler.dump_stats(filename)

    def title(self) -> str:
        if not self.is_active:
            return "Profiler not active"

        return f"View: {float(self.stats.total_tt) * 1000:.2f}ms"  # type: ignore[union-attr]

    def nav_title(self) -> str:
        return "Profiler"

    def nav_subtitle(self) -> str:
        if not self.is_active:
            return "in-active"

        return f"View: {float(self.stats.total_tt) * 1000:.2f}ms"  # type: ignore[union-attr]

    def url(self) -> str:
        return ""

    def content(self) -> str:
        if not self.is_active:
            return "The profiler is not activated, activate it to use it"

        context = {
            "stats": self.stats,
            "function_calls": self.function_calls,
        }
        return self.render("panels/profiler.html", context)
