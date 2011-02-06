import sys
try:
    import cProfile as profile
except ImportError:
    import profile
import functools
import os.path
import pstats

from flask import current_app
from flaskext.debugtoolbar.panels import DebugPanel



class ProfilerDebugPanel(DebugPanel):
    """
    Panel that displays the time a response took with cProfile output.
    """
    name = 'Profiler'

    user_activate = True

    def has_content(self):
        return bool(self.profiler)

    def process_request(self, request):
        if not self.is_active:
            return

        self.profiler = profile.Profile()
        self.stats = None

    def process_view(self, request, view_func, view_kwargs):
        if self.is_active:
            return functools.partial(self.profiler.runcall, view_func)



    def process_response(self, request, response):
        if not self.is_active:
            return False

        if self.profiler is not None:
            self.profiler.disable()
            stats = pstats.Stats(self.profiler)
            function_calls = []
            for func in stats.sort_stats(1).fcn_list:
                current = {}
                info = stats.stats[func]

                # Number of calls
                if info[0] != info[1]:
                    current['ncalls'] = '%d/%d' % (info[1], info[0])
                else:
                    current['ncalls'] = info[1]

                # Total time
                current['tottime'] = info[2] * 1000

                # Quotient of total time divided by number of calls
                if info[1]:
                    current['percall'] = info[2] * 1000 / info[1]
                else:
                    current['percall'] = 0

                # Cumulative time
                current['cumtime'] = info[3] * 1000

                # Quotient of the cumulative time divded by the number of
                # primitive calls.
                if info[0]:
                    current['percall_cum'] = info[3] * 1000 / info[0]
                else:
                    current['percall_cum'] = 0

                # Filename
                filename = pstats.func_std_string(func)
                current['filename_long'] = filename
                current['filename'] = format_fname(filename)
                function_calls.append(current)

            self.stats = stats
            self.function_calls = function_calls
            # destroy the profiler just in case
        return response

    def title(self):
        if not self.is_active:
            return "Profiler not active"
        return 'View: %.2fms' % (float(self.stats.total_tt)*1000,)

    def nav_title(self):
        return 'Profiler'

    def nav_subtitle(self):
        if not self.is_active:
            return "in-active"
        return 'View: %.2fms' % (float(self.stats.total_tt)*1000,)

    def url(self):
        return ''

    def content(self):
        if not self.is_active:
            return "The profiler is not activated, activate it to use it"

        context = {
            'stats': self.stats,
            'function_calls': self.function_calls,
        }
        return self.render('panels/profiler.html', context)


def format_fname(value):
    # If the value is not an absolute path, the it is a builtin or
    # a relative file (thus a project file).
    if not os.path.isabs(value):
        if value.startswith(('{', '<')):
            return value
        if value.startswith('.' + os.path.sep):
            return value
        return '.' + os.path.sep + value

    # If the file is absolute and within the project root handle it as
    # a project file
    if value.startswith(current_app.root_path):
        return "." + value[len(current_app.root_path):]

    # Loop through sys.path to find the longest match and return
    # the relative path from there.
    paths = sys.path
    prefix = None
    prefix_len = 0
    for path in sys.path:
        new_prefix = os.path.commonprefix([path, value])
        if len(new_prefix) > prefix_len:
            prefix = new_prefix
            prefix_len = len(prefix)

    if not prefix.endswith(os.path.sep):
        prefix_len -= 1
    path = value[prefix_len:]
    return '<%s>' % path
