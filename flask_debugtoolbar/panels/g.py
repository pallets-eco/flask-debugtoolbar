from flask import g
from flask_debugtoolbar.panels import DebugPanel

_ = lambda x: x


class GDebugPanel(DebugPanel):
    """
    A panel to display flask.g content.
    """
    name = 'g'
    has_content = True

    def nav_title(self):
        return _('flask.g')

    def title(self):
        return _('flask.g content')

    def url(self):
        return ''
    
    def content(self):
        context = self.context.copy()
        context.update({
            'g_content': g.__dict__
        })
        return self.render('panels/g.html', context)

