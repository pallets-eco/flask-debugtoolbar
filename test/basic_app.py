from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from flask_debugtoolbar import DebugToolbarExtension

app = Flask('basic_app')
app.config['SECRET_KEY'] = 'abc123'
app.config['SQLALCHEMY_RECORD_QUERIES'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

# make sure these are printable in the config panel
app.config['BYTES_VALUE'] = b'\x00'
app.config['UNICODE_VALUE'] = u'\uffff'

toolbar = DebugToolbarExtension(app)
db = SQLAlchemy(app)


class Foo(db.Model):
    __tablename__ = 'foo'
    id = db.Column(db.Integer, primary_key=True)


@app.before_first_request
def setup():
    db.create_all()


@app.route('/')
def index():
    Foo.query.filter_by(id=1).all()
    return render_template('basic_app.html')
