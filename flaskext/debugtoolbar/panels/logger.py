"""
Logger panel (taken from django-debug-toolbar)

"""
import threading
import logging

class ThreadTrackingHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        self.records = {} # a dictionary that maps threads to log records

    def emit(self, record):
        self.get_records().append(record)

    def get_records(self, thread=None):
        """
        Returns a list of records for the provided thread, of if none is provided,
        returns a list for the current thread.
        """
        if thread is None:
            thread = threading.currentThread()
        if thread not in self.records:
            self.records[thread] = []
        return self.records[thread]

    def clear_records(self, thread=None):
        if thread is None:
            thread = threading.currentThread()
        if thread in self.records:
            del self.records[thread]

handler = ThreadTrackingHandler()
logging.root.setLevel(logging.NOTSET)
logging.root.addHandler(handler)
