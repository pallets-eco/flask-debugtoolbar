from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from flask_debugtoolbar import DebugToolbarExtension


app = Flask('basic_app')
app.debug = True
app.config['SECRET_KEY'] = 'abc123'

# make sure these are printable in the config panel
app.config['BYTES_VALUE'] = b'\x00'
app.config['UNICODE_VALUE'] = u'\uffff'

toolbar = DebugToolbarExtension(app)
db = SQLAlchemy(app)


class Foo(db.Model):
    __tablename__ = 'foo'
    id = db.Column(db.Integer, primary_key=True)


@app.route('/')
def index():
    db.create_all()
    Foo.query.filter_by(id=1).all()
    return render_template('basic_app.html')


if __name__ == '__main__':
    app.run()
