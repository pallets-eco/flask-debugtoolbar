import sys
sys.path.insert(0, '.')

from flask import Flask, render_template
from flaskext.script import Manager
from flaskext.sqlalchemy import SQLAlchemy
from flaskext.debugtoolbar import DebugToolbarExtension


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

toolbar = DebugToolbarExtension(app)

class ExampleModel(db.Model):
    __tablename__ = 'examples'
    value = db.Column(db.String(100), primary_key=True)

@app.route('/')
def index():
    app.logger.info("Hello there")
    ExampleModel.query.get(1)
    return render_template('index.html')

if __name__ == "__main__":
    manager = Manager(app)
    manager.run()

