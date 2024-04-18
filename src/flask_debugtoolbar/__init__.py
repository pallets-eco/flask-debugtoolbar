import contextvars
import os
import urllib.parse
import warnings

import flask
from flask import Blueprint, current_app, request, g, send_from_directory, url_for
from flask.globals import request_ctx

from jinja2 import __version__ as __jinja_version__
from jinja2 import Environment, PackageLoader

from flask_debugtoolbar.compat import iteritems
from flask_debugtoolbar.toolbar import DebugToolbar
from flask_debugtoolbar.utils import decode_text, gzip_compress, gzip_decompress

try:
    # Python 3.8+
    from importlib.metadata import version

    __version__ = version("Flask-DebugToolbar")
except ImportError:
    import pkg_resources

    __version__ = pkg_resources.get_distribution("Flask-DebugToolbar").version


module = Blueprint('debugtoolbar', __name__)


def replace_insensitive(string, target, replacement):
    """Similar to string.replace() but is case insensitive
    Code borrowed from:
    http://forums.devshed.com/python-programming-11/case-insensitive-string-replace-490921.html
    """
    no_case = string.lower()
    index = no_case.rfind(target.lower())
    if index >= 0:
        return string[:index] + replacement + string[index + len(target):]
    else:  # no results so return the original string
        return string


def _printable(value):
    try:
        return decode_text(repr(value))
    except Exception as e:
        return '<repr(%s) raised %s: %s>' % (
               object.__repr__(value), type(e).__name__, e)


class DebugToolbarExtension(object):
    _static_dir = os.path.realpath(
        os.path.join(os.path.dirname(__file__), 'static'))

    _toolbar_codes = [200, 201, 400, 401, 403, 404, 405, 500, 501, 502, 503, 504]
    _redirect_codes = [301, 302, 303, 304]

    def __init__(self, app=None):
        self.app = app
        # Support threads running  `flask.copy_current_request_context` without
        # poping toolbar during `teardown_request`
        self.debug_toolbars_var = contextvars.ContextVar('debug_toolbars')
        jinja_extensions = ['jinja2.ext.i18n']

        if __jinja_version__[0] == '2':
            jinja_extensions.append('jinja2.ext.with_')

        # Configure jinja for the internal templates and add url rules
        # for static data
        self.jinja_env = Environment(
            autoescape=True,
            extensions=jinja_extensions,
            loader=PackageLoader(__name__, 'templates'))
        self.jinja_env.filters['urlencode'] = urllib.parse.quote_plus
        self.jinja_env.filters['printable'] = _printable
        self.jinja_env.globals['url_for'] = url_for

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        for k, v in iteritems(self._default_config(app)):
            app.config.setdefault(k, v)

        if not app.config['DEBUG_TB_ENABLED']:
            return

        if not app.config.get('SECRET_KEY'):
            raise RuntimeError(
                "The Flask-DebugToolbar requires the 'SECRET_KEY' config "
                "var to be set")

        DebugToolbar.load_panels(app)

        app.before_request(self.process_request)
        app.after_request(self.process_response)
        app.teardown_request(self.teardown_request)

        # Monkey-patch the Flask.dispatch_request method
        app.dispatch_request = self.dispatch_request

        app.add_url_rule('/_debug_toolbar/static/<path:filename>',
                         '_debug_toolbar.static', self.send_static_file)

        app.register_blueprint(module, url_prefix='/_debug_toolbar/views')

    def _default_config(self, app):
        return {
            'DEBUG_TB_ENABLED': app.debug,
            'DEBUG_TB_HOSTS': (),
            'DEBUG_TB_INTERCEPT_REDIRECTS': True,
            'DEBUG_TB_PANELS': (
                'flask_debugtoolbar.panels.versions.VersionDebugPanel',
                'flask_debugtoolbar.panels.timer.TimerDebugPanel',
                'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
                'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
                'flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel',
                'flask_debugtoolbar.panels.template.TemplateDebugPanel',
                'flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel',
                'flask_debugtoolbar.panels.logger.LoggingPanel',
                'flask_debugtoolbar.panels.route_list.RouteListDebugPanel',
                'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
                'flask_debugtoolbar.panels.g.GDebugPanel',
            ),
            'SQLALCHEMY_RECORD_QUERIES': app.debug,
        }

    def dispatch_request(self):
        """Modified version of Flask.dispatch_request to call process_view."""
        req = request_ctx.request
        app = current_app

        if req.routing_exception is not None:
            app.raise_routing_exception(req)

        rule = req.url_rule

        # if we provide automatic options for this URL and the
        # request came with the OPTIONS method, reply automatically
        if getattr(rule, 'provide_automatic_options', False) \
           and req.method == 'OPTIONS':
            return app.make_default_options_response()

        # otherwise dispatch to the handler for that endpoint
        view_func = app.view_functions[rule.endpoint]
        view_func = self.process_view(app, view_func, req.view_args)

        return view_func(**req.view_args)

    def _show_toolbar(self):
        """Return a boolean to indicate if we need to show the toolbar."""
        if request.blueprint == 'debugtoolbar':
            return False

        hosts = current_app.config['DEBUG_TB_HOSTS']
        if hosts and request.remote_addr not in hosts:
            return False

        return True

    def send_static_file(self, filename):
        """Send a static file from the flask-debugtoolbar static directory."""
        return send_from_directory(self._static_dir, filename)

    def process_request(self):
        g.debug_toolbar = self

        if not self._show_toolbar():
            return

        real_request = request._get_current_object()
        self.debug_toolbars_var.set({})
        self.debug_toolbars_var.get()[real_request] = (
            DebugToolbar(real_request, self.jinja_env))

        for panel in self.debug_toolbars_var.get()[real_request].panels:
            panel.process_request(real_request)

    def process_view(self, app, view_func, view_kwargs):
        """ This method is called just before the flask view is called.
        This is done by the dispatch_request method.
        """
        real_request = request._get_current_object()
        try:
            toolbar = self.debug_toolbars_var.get({})[real_request]
        except KeyError:
            return view_func

        for panel in toolbar.panels:
            new_view = panel.process_view(real_request, view_func, view_kwargs)
            if new_view:
                view_func = new_view

        return view_func

    def process_response(self, response):
        real_request = request._get_current_object()
        if real_request not in self.debug_toolbars_var.get({}):
            return response

        # Intercept http redirect codes and display an html page with a
        # link to the target.
        if current_app.config['DEBUG_TB_INTERCEPT_REDIRECTS']:
            if response.status_code in self._redirect_codes:
                redirect_to = response.location
                redirect_code = response.status_code
                if redirect_to:
                    content = self.render('redirect.html', {
                        'redirect_to': redirect_to,
                        'redirect_code': redirect_code
                    })
                    response.content_length = len(content)
                    response.location = None
                    response.response = [content]
                    response.status_code = 200

        # If the http response code is an allowed code then we process to add the
        # toolbar to the returned html response.
        if not (response.status_code in self._toolbar_codes and
                response.is_sequence and
                response.headers['content-type'].startswith('text/html')):
            return response

        content_encoding = response.headers.get('Content-Encoding')
        if content_encoding and 'gzip' in content_encoding:
            response_html = gzip_decompress(response.data).decode()
        else:
            response_html = response.get_data(as_text=True)

        no_case = response_html.lower()
        body_end = no_case.rfind('</body>')

        if body_end >= 0:
            before = response_html[:body_end]
            after = response_html[body_end:]
        elif no_case.startswith('<!doctype html>'):
            before = response_html
            after = ''
        else:
            warnings.warn('Could not insert debug toolbar.'
                          ' </body> tag not found in response.')
            return response

        toolbar = self.debug_toolbars_var.get()[real_request]

        for panel in toolbar.panels:
            panel.process_response(real_request, response)

        toolbar_html = toolbar.render_toolbar()

        content = ''.join((before, toolbar_html, after))
        content = content.encode('utf-8')
        if content_encoding and 'gzip' in content_encoding:
            content = gzip_compress(content)
        response.response = [content]
        response.content_length = len(content)

        return response

    def teardown_request(self, exc):
        # debug_toolbars_var won't be set under `flask.copy_current_request_context`
        self.debug_toolbars_var.get({}).pop(request._get_current_object(), None)

    def render(self, template_name, context):
        template = self.jinja_env.get_template(template_name)
        return template.render(**context)
