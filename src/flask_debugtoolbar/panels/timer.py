from __future__ import annotations

import time

from werkzeug import Request
from werkzeug import Response

from . import DebugPanel

try:
    import resource

    HAVE_RESOURCE = True
except ImportError:
    HAVE_RESOURCE = False


class TimerDebugPanel(DebugPanel):
    """Panel that displays the time a response took in milliseconds."""

    name = "Timer"
    has_content = HAVE_RESOURCE

    def process_request(self, request: Request) -> None:
        self._start_time = time.time()

        if HAVE_RESOURCE:
            self._start_rusage = resource.getrusage(resource.RUSAGE_SELF)

    def process_response(self, request: Request, response: Response) -> None:
        self.total_time: float = (time.time() - self._start_time) * 1000

        if HAVE_RESOURCE:
            self._end_rusage = resource.getrusage(resource.RUSAGE_SELF)

    def nav_title(self) -> str:
        return "Time"

    def nav_subtitle(self) -> str:
        if not HAVE_RESOURCE:
            return f"TOTAL: {self.total_time:0.2f}ms"

        utime = self._end_rusage.ru_utime - self._start_rusage.ru_utime
        stime = self._end_rusage.ru_stime - self._start_rusage.ru_stime
        return f"CPU: {(utime + stime) * 1000.0:0.2f}ms ({self.total_time:0.2f}ms)"

    def title(self) -> str:
        return "Resource Usage"

    def url(self) -> str:
        return ""

    def _elapsed_ru(self, name: str) -> float:
        return getattr(self._end_rusage, name) - getattr(self._start_rusage, name)  # type: ignore[no-any-return]

    def content(self) -> str:
        utime = 1000 * self._elapsed_ru("ru_utime")
        stime = 1000 * self._elapsed_ru("ru_stime")
        vcsw = self._elapsed_ru("ru_nvcsw")
        ivcsw = self._elapsed_ru("ru_nivcsw")
        # minflt = self._elapsed_ru("ru_minflt")
        # majflt = self._elapsed_ru("ru_majflt")

        # these are documented as not meaningful under Linux.  If you're running BSD
        # feel free to enable them, and add any others that I hadn't gotten to before
        # I noticed that I was getting nothing but zeroes and that the docs agreed. :-(
        # blkin = self._elapsed_ru("ru_inblock")
        # blkout = self._elapsed_ru("ru_oublock")
        # swap = self._elapsed_ru("ru_nswap")
        # rss = self._end_rusage.ru_maxrss
        # srss = self._end_rusage.ru_ixrss
        # urss = self._end_rusage.ru_idrss
        # usrss = self._end_rusage.ru_isrss
        rows = (
            ("User CPU time", f"{utime:0.3f} msec"),
            ("System CPU time", f"{stime:0.3f} msec"),
            ("Total CPU time", f"{(utime + stime):0.3f} msec"),
            ("Elapsed time", f"{self.total_time:0.3f} msec"),
            ("Context switches", f"{vcsw} voluntary, {ivcsw} involuntary"),
            # (
            #     "Memory use",
            #     f"{rss} max RSS, {srss} shared, {urss + usrss} unshared",
            # ),
            # ("Page faults", f"{minflt} no i/o, {majflt} requiring i/o"),
            # ("Disk operations", f"{blkin} in, {blkout} out, {swap} swapout"),
        )
        context = self.context.copy()
        context.update(
            {
                "rows": rows,
            }
        )
        return self.render("panels/timer.html", context)
