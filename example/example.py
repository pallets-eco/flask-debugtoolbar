from flask import Flask, render_template
from flaskext.script import Manager
from flaskext.debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
toolbar = DebugToolbarExtension(app)

@app.route('/')
def index():
    app.logger.info("Hello there")

    return render_template('index.html')

if __name__ == "__main__":
    manager = Manager(app)
    manager.run()

