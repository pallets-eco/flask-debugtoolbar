try:
    import cProfile as profile
except ImportError:
    import profile
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

        # Monkey-patch Flask.dispatch_request for profiling
        org_dispatch_request = current_app.dispatch_request
        def dispatch_request():
            content = self.profiler.runcall(org_dispatch_request)
            current_app.dispatch_request = org_dispatch_request
            return content
        current_app.dispatch_request = dispatch_request

    def process_response(self, request, response):
        if not self.is_active:
            return False

        if self.profiler is not None:
            self.profiler.disable()
            stats = pstats.Stats(self.profiler)
            function_calls = []
            for func in stats.strip_dirs().sort_stats(1).fcn_list:
                current = []
                if stats.stats[func][0] != stats.stats[func][1]:
                    current.append('%d/%d' % (stats.stats[func][1], stats.stats[func][0]))
                else:
                    current.append(stats.stats[func][1])
                current.append(stats.stats[func][2]*1000)
                if stats.stats[func][1]:
                    current.append(stats.stats[func][2]*1000/stats.stats[func][1])
                else:
                    current.append(0)
                current.append(stats.stats[func][3]*1000)
                if stats.stats[func][0]:
                    current.append(stats.stats[func][3]*1000/stats.stats[func][0])
                else:
                    current.append(0)
                current.append(pstats.func_std_string(func))
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

