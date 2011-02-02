import os

from flask import request_finished, request_started, request
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
    _static_dir = os.path.join(os.path.dirname(__file__), 'static')

    def __init__(self, app):
        self.app = app
        self.debug_toolbars = {}

        request_started.connect(self.process_request, app)
        request_finished.connect(self.process_response, app)

        # Configure jinja for the internal templates and add url rules
        # for static data
        self.jinja_env = Environment(loader=PackageLoader(__name__, 'templates'))
        app.url_map.add(Submount('/_debug_toolbar', [
            Rule('/static/<path:filename>', endpoint='_debug_toolbar.static'),
        ]))
        app.view_functions['_debug_toolbar.static'] = self.send_static_file

    def send_static_file(self, filename):
        return send_from_directory(self._static_dir, filename)

    def process_request(self, app):
        self.debug_toolbars[request] = DebugToolbar(request, self.jinja_env)
        for panel in self.debug_toolbars[request].panels:
            panel.process_request(request)

    def process_response(self, sender, response):
        if request not in self.debug_toolbars:
            return response

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

