from distutils.sysconfig import get_python_lib

from flask import __version__ as flask_version
from flask_debugtoolbar.panels import DebugPanel

_ = lambda x: x

class VersionDebugPanel(DebugPanel):
    """
    Panel that displays the Flask version.
    """
    name = 'Version'
    has_content = True

    def nav_title(self):
        return _('Versions')

    def nav_subtitle(self):
        return 'Flask %s' % flask_version

    def url(self):
        return ''

    def title(self):
        return _('Versions')

    def content(self):
        try:
            import pkg_resources
        except ImportError:
            context = self.context.copy()
            context.update({
                'packages': []
                })
        else:
            active_packages = pkg_resources.WorkingSet()
            _pkgs = dict([(p.project_name, p) for p in active_packages])
            packages = [_pkgs[key] for key in sorted(_pkgs.iterkeys())]
            for package in packages:
                package.develop_mode = not (package.location.lower().startswith(get_python_lib().lower()))

            context = self.context.copy()
            context.update({
                'packages': packages
            })

        return self.render('panels/versions.html', context)