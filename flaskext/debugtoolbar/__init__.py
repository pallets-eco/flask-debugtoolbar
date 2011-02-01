import os

from flask import request_finished
from flask.helpers import send_from_directory
from jinja2 import Environment, PackageLoader
from werkzeug.routing import Rule, Submount

from .panels.logger import handler
from .views import views_module


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


class DebugToolbar(object):
    _static_dir = os.path.join(os.path.dirname(__file__), 'static')

    def __init__(self, app):
        self.jinja_env = Environment(loader=PackageLoader(__name__, 'templates'))
        request_finished.connect(self.process_response, app)

        app.url_map.add(Submount('/_debug_toolbar', [
            Rule('/static/<path:filename>', endpoint='_debug_toolbar.static'),
            Rule('/css/main.css', endpoint='_debug_toolbar.example')
        ]))

        app.register_module(views_module)
        app.view_functions['_debug_toolbar.static'] = self.send_static_file

    def send_static_file(self, filename):
        return send_from_directory(self._static_dir, filename)

    def render_toolbar(self):
        template = self.jinja_env.get_template('base.html')
        content = template.render()
        return content

    def process_response(self, sender, response):
        if response.is_sequence:
            response_html = response.data
            toolbar_html = self.render_toolbar()

            response.response = [
                replace_insensitive(
                    response_html,
                    '</body>',
                    toolbar_html + '</body>')]
