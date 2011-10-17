from flask import template_rendered
from flask_debugtoolbar.panels import DebugPanel

_ = lambda x: x

class TemplateDebugPanel(DebugPanel):
    """
    Panel that displays the time a response took in milliseconds.
    """
    name = 'Template'
    has_content = True

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.templates = []
        template_rendered.connect(self._store_template_info)

    def _store_template_info(self, sender, **kwargs):
        self.templates.append(kwargs)

    def process_request(self, request):
        pass

    def process_response(self, request, response):
        pass

    def nav_title(self):
        return _('Templates')

    def nav_subtitle(self):
        return "%d rendered" % len(self.templates)

    def title(self):
        return _('Templates')

    def url(self):
        return ''

    def content(self):
        return self.render('panels/template.html', {
            'templates': self.templates
        })


