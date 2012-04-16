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
        if current_app.config.get('DEBUG_TB_PROFILER_MEMORY_ENABLED'):
            self.track_usage = True
        else:
            self.track_usage = False

    def has_content(self):
        if self.track_usage:
            return self.summary is not None and self.tracked is not None
        else:
            return self.summary is not None

    def nav_title(self):
        if self.is_active:
            return 'Memory'
        else:
            return 'Memory inactive'

    def title(self):
        return self.nav_subtitle()

    def nav_subtitle(self):
        if self.is_active:
            overall = sum(map(itemgetter(2), self.summary))
            if self.track_usage:
                generated = sum(map(itemgetter(2), self.tracked))
                return 'Usage: {} ({})'.format(pretty_bytes(overall),
                                               pretty_bytes(generated))
            else:
                return 'Usage: {}'.format(pretty_bytes(overall))
        else:
            return 'Deactivated'

    def url(self):
        return ''

    def process_request(self, request):
        if not self.is_active:
            return
        if self.track_usage:
            self.tracker = tracker.SummaryTracker()
            # drop previous diff, we want to see what was
            # created during request processing
            self.tracker.diff()

    def process_response(self, request, response):
        if not self.is_active:
            return False
        if self.track_usage:
            self.tracked = self.tracker.diff()
        self.summary = summary.summarize(muppy.get_objects())

    def content(self):
        if not self.is_active:
            return 'Memory profiler not activated'
        # objects = muppy.filter(muppy.get_objects(), Type=types.ClassType)
        self.context['summary'] = sorted(self.summary, key=itemgetter(2), reverse=True)
        self.context['tracked'] = self.tracked
        return self.render('panels/memory.html', self.context)
