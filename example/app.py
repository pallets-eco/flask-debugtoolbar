# Run using: `flask run` after setting env vars

from flask import Flask, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
import os

app = Flask(__name__)

# Use a cross-platform-safe DB path
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "test.db")

app.config["SECRET_KEY"] = "asd"
app.config["SQLALCHEMY_RECORD_QUERIES"] = True
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = True
app.config["DEBUG"] = True  # ✅ Ensure app runs in debug mode
app.debug = True            # ✅ Double-safe flag for debug

db = SQLAlchemy(app)
toolbar = DebugToolbarExtension(app)

# Model
class ExampleModel(db.Model):
    __tablename__ = "examples"
    value = db.Column(db.String(100), primary_key=True)

# Routes
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

# Create the database
with app.app_context():
    db.create_all()
