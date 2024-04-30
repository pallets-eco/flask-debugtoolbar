import datetime
import logging
import threading

from ..utils import format_fname
from . import DebugPanel


class ThreadTrackingHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = {}  # a dictionary that maps threads to log records

    def emit(self, record):
        self.get_records().append(record)

    def get_records(self, thread=None):
        """
        Returns a list of records for the provided thread, of if none is
        provided, returns a list for the current thread.
        """
        if thread is None:
            thread = threading.current_thread()

        if thread not in self.records:
            self.records[thread] = []

        return self.records[thread]

    def clear_records(self, thread=None):
        if thread is None:
            thread = threading.current_thread()

        if thread in self.records:
            del self.records[thread]


handler = None
_init_lock = threading.Lock()


def _init_once():
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

    def process_request(self, request):
        _init_once()
        handler.clear_records()

    def get_and_delete(self):
        records = handler.get_records()
        handler.clear_records()
        return records

    def nav_title(self):
        return "Logging"

    def nav_subtitle(self):
        num_records = len(handler.get_records())
        plural = "message" if num_records == 1 else "messages"
        return f"{num_records} {plural}"

    def title(self):
        return "Log Messages"

    def url(self):
        return ""

    def content(self):
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
