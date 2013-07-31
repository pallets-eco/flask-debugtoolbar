import urllib

from flask import url_for, current_app
from werkzeug.utils import import_string


class DebugToolbar(object):

    _cached_panel_classes = {}

    def __init__(self, request, jinja_env):
        self.jinja_env = jinja_env
        self.request = request
        self.panels = []

        self.template_context = {
            'static_path': url_for('_debug_toolbar.static', filename='')
        }

        self.create_panels()

    def create_panels(self):
        """
        Populate debug panels
        """
        activated = self.request.cookies.get('fldt_active', '')
        activated = urllib.unquote(activated).split(';')

        for panel_path in current_app.config['DEBUG_TB_PANELS']:
            panel_class = self._import_panel(panel_path)
            if panel_class is None:
                continue

            panel_instance = panel_class(jinja_env=self.jinja_env, context=self.template_context)

            if panel_instance.dom_id() in activated:
                panel_instance.is_active = True
            self.panels.append(panel_instance)

    def render_toolbar(self):
        context = self.template_context.copy()
        context.update({'panels': self.panels})

        template = self.jinja_env.get_template('base.html')
        return template.render(**context)

    def _import_panel(self, path):
        cache = self._cached_panel_classes

        try:
            return cache[path]
        except KeyError:
            pass

        try:
            panel_class = import_string(path)
        except ImportError, e:
            current_app.logger.warning('Disabled %s due to ImportError: %s', path, e)
            panel_class = None

        cache[path] = panel_class
        return panel_class
