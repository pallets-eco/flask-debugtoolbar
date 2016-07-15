import subprocess

from flask_debugtoolbar.panels import DebugPanel

_ = lambda x: x


class GitDebugPanel(DebugPanel):
    """
    Panel that displays the Git information.
    """
    name = 'Git'
    has_content = True
    _branch = ''
    _commit = ''
    _status = []

    @property
    def branch(self):
        if self._branch == '':
            try:
                branch = subprocess.check_output(['git', 'branch', '-q'])
                self._branch = next(l.split()[1] for l in branch.splitlines() if l.lstrip()[0] == '*')
            except (subprocess.CalledProcessError, OSError, IOError):
                pass
        return self._branch

    @property
    def commit(self):
        if self._commit == '':
            try:
                self._commit = subprocess.check_output('git log | head -n 1', shell=True).split()[1]
            except (subprocess.CalledProcessError, OSError, IOError, KeyError):
                pass
        return self._commit

    @property
    def status(self):
        if not self._status:
            try:
                self._status = subprocess.check_output(['git', 'status', '--porcelain']).splitlines()
            except (subprocess.CalledProcessError, OSError, IOError):
                pass
        return self._status

    def nav_title(self):
        return _('Git')

    def nav_subtitle(self):
        return self.branch

    def url(self):
        return ''

    def title(self):
        return _('Git')

    def content(self):
        return self.render('panels/git.html', {
            'branch': self.branch,
            'commit': self.commit,
            'status': self.status
        })
