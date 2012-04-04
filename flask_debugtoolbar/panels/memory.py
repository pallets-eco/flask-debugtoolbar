from flask_debugtoolbar import module
from flask_debugtoolbar.panels import DebugPanel
from flask import current_app
from pympler import muppy, summary, tracker
import types
from operator import itemgetter



def pretty_bytes(bytes):
    multipliers = [(1, 'b'),
                   (10**3, 'K'),
                   (10**6, 'M'),
                   (10**9, 'G')]
    for multiplier, suffix in multipliers:
        if bytes / multiplier < 10**3:
            return '{}{}'.format(bytes / multiplier, suffix)
    else:
        return '{}b'.format(bytes)



class MemoryProfilerDebugPanel(DebugPanel):

    name = 'Memory'
    user_activate = True

    def __init__(self, jinja_env, context={}):
        DebugPanel.__init__(self, jinja_env, context=context)
        self.summary = None
        self.tracker = None
        self.tracked = None

    def has_content(self):
        return self.summary is not None and self.tracked is not None

    def nav_title(self):
        if self.is_active:
            return 'Memory'
        else:
            return 'Memory inactive'

    def title(self):
        return self.nav_subtitle()

    def nav_subtitle(self):
        if self.is_active:
            print(dir(self.tracked))
            generated = sum(map(itemgetter(2), self.tracked))
            overall = sum(map(itemgetter(2), self.summary))
            return 'Usage: {} ({})'.format(pretty_bytes(generated),
                                           pretty_bytes(overall))
        else:
            return 'Deactivated'

    def url(self):
        return ''

    def process_request(self, request):
        if not self.is_active:
            return
        self.tracker = tracker.SummaryTracker()
        # drop previous diff, we want to see what was
        # created during request processing
        self.tracker.diff()

    def process_response(self, request, response):
        if not self.is_active:
            return False
        self.tracked = self.tracker.diff()
        self.summary = summary.summarize(muppy.get_objects())

    def content(self):
        if not self.is_active:
            return 'Memory profiler not activated'
        # objects = muppy.filter(muppy.get_objects(), Type=types.ClassType)
        self.context['summary'] = sorted(self.summary, key=itemgetter(2), reverse=True)
        self.context['tracked'] = self.tracked
        return self.render('panels/memory.html', self.context)
