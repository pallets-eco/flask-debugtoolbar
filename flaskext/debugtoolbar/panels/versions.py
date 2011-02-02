import pkg_resources

from flaskext.debugtoolbar.panels import DebugPanel

_ = lambda x: x

flask_version = pkg_resources.get_distribution('Flask').version

class VersionDebugPanel(DebugPanel):
    """
    Panel that displays the Django version.
    """
    name = 'Version'
    has_content = False

    def nav_title(self):
        return _('Versions')

    def nav_subtitle(self):
        return 'Flask %s' % flask_version

    def url(self):
        return ''

    def title(self):
        return _('Versions')

    def content(self):
        return None


