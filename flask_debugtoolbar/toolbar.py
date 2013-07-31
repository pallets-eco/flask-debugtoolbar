import urllib

from flask import url_for, current_app


class DebugToolbar(object):

    def __init__(self, request, jinja_env):
        self.jinja_env = jinja_env
        self.request = request
        self.panels = []

        self.template_context = {
            'static_path': url_for('_debug_toolbar.static', filename='')
        }

        self.create_panels()

    def _load_panels(self):
        for panel_path in current_app.config['DEBUG_TB_PANELS']:
            dot = panel_path.rindex('.')
            panel_module, panel_classname = panel_path[:dot], panel_path[dot+1:]

            try:
                mod = __import__(panel_module, {}, {}, [''])
            except ImportError, e:
                app.logger.warning('Disabled %s due to ImportError: %s', panel_classname, e)
                continue
            panel_class = getattr(mod, panel_classname)
            yield panel_class(jinja_env=self.jinja_env, context=self.template_context)

    def create_panels(self):
        """
        Populate debug panels
        """
        activated = self.request.cookies.get('fldt_active', '')
        activated = urllib.unquote(activated).split(';')

        for panel_instance in self._load_panels():
            if panel_instance.dom_id() in activated:
                panel_instance.is_active = True
            self.panels.append(panel_instance)

    def render_toolbar(self):
        context = self.template_context.copy()
        context.update({'panels': self.panels})

        template = self.jinja_env.get_template('base.html')
        return template.render(**context)


