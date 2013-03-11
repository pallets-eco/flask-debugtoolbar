from __future__ import absolute_import, with_statement

import datetime
import logbook
try:
    import threading
except ImportError:
    threading = None

from flask_debugtoolbar.panels import DebugPanel
from flask_debugtoolbar.utils import format_fname


_ = lambda x: x


class ThreadTrackingHandler(logbook.Handler):
    def __init__(self):
        if threading is None:
            raise NotImplementedError("threading module is not available, \
                the logbook panel cannot be used without it")
        super(ThreadTrackingHandler, self).__init__()
        self.records = {} # a dictionary that maps threads to log records

    def emit(self, record):
        record.pull_information()
        thread = threading.currentThread()
        self.records.setdefault(thread, [])
        self.records[thread].append(record)

    def get_records(self, thread=None):
        if thread is None:
            thread = threading.currentThread()
        self.records.setdefault(thread, [])
        return self.records[thread]

    def clear_records(self, thread=None):
        if thread is None:
            thread = threading.currentThread()
        if thread in self.records:
            del self.records[thread]


handler = None
_init_lock = threading.Lock()


def _init_once():
  # Initialize the logbook handler once.
  global handler
  if handler is not None:
    return
  with _init_lock:
    if handler is not None:
      return
    handler = ThreadTrackingHandler()
    handler.push_application()


class LogbookPanel(DebugPanel):
    name = 'Logbook'
    has_content = True

    def process_request(self, request):
        _init_once()
        handler.clear_records()

    def get_and_delete(self):
        records = handler.get_records()
        handler.clear_records()
        return records

    def nav_title(self):
        return _("Logbook")

    def nav_subtitle(self):
        # FIXME l10n: use ngettext
        return "%s message%s" % (
            (len(handler.get_records()),
            (len(handler.get_records()) == 1) and '' or 's'))

    def title(self):
        return _('Log Messages')

    def url(self):
        return ''

    def content(self):
        records = []
        for record in self.get_and_delete():
            records.append({
                'level': record.level_name,
                'channel': record.channel,
                'message': record.message,
                'time': record.time.strftime('%Y-%m-%d %H:%M:%S'),
                'file': format_fname(record.filename),
                'file_long': record.filename,
                'line': record.lineno
            })

        context = self.context.copy()
        context.update({'records': records})

        return self.render('panels/logbook.html', context)


