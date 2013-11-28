# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension

app = Flask('basic_app')
app.debug = True
app.config['SECRET_KEY'] = 'abc123'

# make sure these are printable in the config panel
app.config['BYTES_VALUE'] = b'\x00'
app.config['UNICODE_VALUE'] = u'\uffff'

toolbar = DebugToolbarExtension(app)


@app.route('/')
def index():
    return render_template('basic_app.html')
