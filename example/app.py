# Run using: `FLASK_DEBUG=True flask run`

from flask import Flask
from flask import redirect
from flask import render_template
from flask import url_for
from flask_sqlalchemy import SQLAlchemy

from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = True
# app.config['DEBUG_TB_PANELS'] = (
#    'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
#    'flask_debugtoolbar.panels.logger.LoggingPanel',
#    'flask_debugtoolbar.panels.timer.TimerDebugPanel',
# )
# app.config['DEBUG_TB_HOSTS'] = ('127.0.0.1', '::1' )
app.config["SECRET_KEY"] = "asd"
app.config["SQLALCHEMY_RECORD_QUERIES"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
# This is no longer needed for Flask-SQLAlchemy 3.0+, if you're using 2.X you'll want to define this:
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
toolbar = DebugToolbarExtension(app)


class ExampleModel(db.Model):
    __tablename__ = "examples"
    value = db.Column(db.String(100), primary_key=True)


@app.route("/")
def index():
    app.logger.info("Hello there")
    ExampleModel.query.get(1)
    return render_template("index.html")


@app.route("/redirect")
def redirect_example():
    response = redirect(url_for("index"))
    response.set_cookie("test_cookie", "1")
    return response


with app.app_context():
    db.create_all()
