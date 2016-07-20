from flask import g
from flask_debugtoolbar.panels import DebugPanel
from flask_debugtoolbar import module
import jinja2

mails = {}
last_index = 0

def _add_mail(message, app):
    global mails, last_index
    mails.update({last_index: message})
    last_index += 1

try:
    import flask_mail
    flask_mail.email_dispatched.connect(_add_mail)
except:
    pass

@module.route('/mail/remove/<int:key>', methods=['GET', 'POST'])
def remove_mail(key=None):
    global mails
    del mails[key]
    return "ok"

@module.route('/mail/remove/all', methods=['GET', 'POST'])
def remove_all_mails():
    global mails
    mails = {}
    return "ok"


class MailDebugPanel(DebugPanel):
    """
    Panel that displays the mails send from flask_mail.
    """
    name = 'Mail'
    
    try:  # if resource module not available, don't show content panel
        flask_mail
    except NameError:
        has_content = False
        has_resource = False
    else:
        has_content = True
        has_resource = True

    def process_request(self, request):
        pass

    def process_response(self, request, response):
        pass
    
    def nav_title(self):
        return 'Mails'

    def nav_subtitle(self):
        if len(mails) == 1:
            return '1 Mail'
        else:
            return '%d Mails' % (len(mails))

    def title(self):
        return 'Mails'

    def url(self):
        return ''

    def content(self):
        global mails
        context = self.context.copy()
        context.update({
            'mails': mails,
        })
 
        return self.render('panels/mail.html', context)


