import os
from sysconfig import get_path

from flask_debugtoolbar.panels import DebugPanel

try:
    # Python 3.8+
    from importlib.metadata import version

    flask_version = version('flask')

except ImportError:
    import pkg_resources

    flask_version = pkg_resources.get_distribution('flask').version

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
            import importlib.metadata
        except ImportError:
            packages = []
        else:
            packages_metadata = [p.metadata for p in importlib.metadata.distributions()]
            packages = sorted(packages_metadata, key=lambda p: p['Name'].lower())

        return self.render('panels/versions.html', {
            'packages': packages,
            'python_lib_dir': os.path.normpath(get_path('platlib')),
        })
