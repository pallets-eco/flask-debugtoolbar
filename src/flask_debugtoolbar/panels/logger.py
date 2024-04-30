from __future__ import annotations

import datetime
import logging
import threading

from werkzeug import Request

from ..utils import format_fname
from . import DebugPanel


class ThreadTrackingHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        # a dictionary that maps threads to log records
        self.records: dict[threading.Thread, list[logging.LogRecord]] = {}

    def emit(self, record: logging.LogRecord) -> None:
        self.get_records().append(record)

    def get_records(
        self, thread: threading.Thread | None = None
    ) -> list[logging.LogRecord]:
        """
        Returns a list of records for the provided thread, of if none is
        provided, returns a list for the current thread.
        """
        if thread is None:
            thread = threading.current_thread()

        if thread not in self.records:
            self.records[thread] = []

        return self.records[thread]

    def clear_records(self, thread: threading.Thread | None = None) -> None:
        if thread is None:
            thread = threading.current_thread()

        if thread in self.records:
            del self.records[thread]


handler: ThreadTrackingHandler = None  # type: ignore[assignment]
_init_lock = threading.Lock()


def _init_once() -> None:
    global handler

    if handler is not None:
        return

    with _init_lock:
        if handler is not None:
            return

        # Call werkzeug's internal logging to make sure it gets configured
        # before we add our handler.  Otherwise werkzeug will see our handler
        # and not configure console logging for the request log.
        # Werkzeug's default log level is INFO so this message probably won't
        # be seen.
        from werkzeug._internal import _log

        _log("debug", "Initializing Flask-DebugToolbar log handler")
        handler = ThreadTrackingHandler()
        logging.root.addHandler(handler)


class LoggingPanel(DebugPanel):
    name = "Logging"
    has_content = True

    def process_request(self, request: Request) -> None:
        _init_once()
        handler.clear_records()

    def get_and_delete(self) -> list[logging.LogRecord]:
        records = handler.get_records()
        handler.clear_records()
        return records

    def nav_title(self) -> str:
        return "Logging"

    def nav_subtitle(self) -> str:
        num_records = len(handler.get_records())
        plural = "message" if num_records == 1 else "messages"
        return f"{num_records} {plural}"

    def title(self) -> str:
        return "Log Messages"

    def url(self) -> str:
        return ""

    def content(self) -> str:
        records = []

        for record in self.get_and_delete():
            records.append(
                {
                    "message": record.getMessage(),
                    "time": datetime.datetime.fromtimestamp(record.created),
                    "level": record.levelname,
                    "file": format_fname(record.pathname),
                    "file_long": record.pathname,
                    "line": record.lineno,
                }
            )

        context = self.context.copy()
        context.update({"records": records})
        return self.render("panels/logger.html", context)
