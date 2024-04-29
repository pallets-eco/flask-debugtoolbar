import importlib.metadata
import os
from sysconfig import get_path

from flask_debugtoolbar.panels import DebugPanel

flask_version = importlib.metadata.version("flask")

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
        packages_metadata = [p.metadata for p in importlib.metadata.distributions()]
        packages = sorted(packages_metadata, key=lambda p: p['Name'].lower())

        return self.render('panels/versions.html', {
            'packages': packages,
            'python_lib_dir': os.path.normpath(get_path('platlib')),
        })
