import os

from flask import request
from flask import signals
from flask.helpers import send_from_directory
from jinja2 import Environment, PackageLoader
from werkzeug.routing import Rule, Submount

from flaskext.debugtoolbar.toolbar import DebugToolbar

def replace_insensitive(string, target, replacement):
    """
    Similar to string.replace() but is case insensitive
    Code borrowed from: http://forums.devshed.com/python-programming-11/case-insensitive-string-replace-490921.html
    """
    no_case = string.lower()
    index = no_case.rfind(target.lower())
    if index >= 0:
        return string[:index] + replacement + string[index + len(target):]
    else: # no results so return the original string
        return string


class DebugToolbarExtension(object):
    _static_dir = os.path.realpath(
        os.path.join(os.path.dirname(__file__), 'static'))

    _redirect_codes = [301, 302, 303, 304]

    def __init__(self, app):
        self.app = app
        self.debug_toolbars = {}

        signals.request_started.connect(self.process_request, app)
        signals.request_finished.connect(self.process_response, app)

        # Configure jinja for the internal templates and add url rules
        # for static data
        self.jinja_env = Environment(
            extensions=['jinja2.ext.i18n'],
            loader=PackageLoader(__name__, 'templates'))

        app.add_url_rule('/_debug_toolbar/static/<path:filename>',
            '_debug_toolbar.static', self.send_static_file)

    def send_static_file(self, filename):
        return send_from_directory(self._static_dir, filename)

    def process_request(self, app):
        self.debug_toolbars[request] = DebugToolbar(request, self.jinja_env)
        for panel in self.debug_toolbars[request].panels:
            panel.process_request(request)

    def process_view(self, app, template, context):
        if request in self.debug_toolbars:
            for panel in self.debug_toolbars[request].panels:
                panel.process_view(request, template, [], context)

    def process_response(self, sender, response):
        if request not in self.debug_toolbars:
            return response

        if self.debug_toolbars[request].config['DEBUG_TB_INTERCEPT_REDIRECTS']:
            if response.status_code in self._redirect_codes:
                redirect_to = response.location
                redirect_code = response.status_code
                if redirect_to:
                    response.location = None
                    response.status_code = 200
                    response.response = [
                        self.render('redirect.html', {
                            'redirect_to': redirect_to,
                            'redirect_code': redirect_code})]

        if response.status_code == 200:
            for panel in self.debug_toolbars[request].panels:
                panel.process_response(request, response)

            if response.is_sequence:
                response_html = response.data
                toolbar_html = self.debug_toolbars[request].render_toolbar()
                response.response = [
                    replace_insensitive(
                        response_html,
                        '</body>',
                        toolbar_html + '</body>')]

    def render(self, template_name, context):
        template = self.jinja_env.get_template(template_name)
        return template.render(**context)
