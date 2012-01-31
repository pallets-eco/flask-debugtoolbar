Flask Debug-toolbar
===================

This is a port of the excellent `django-debug-toolbar <github.com/robhudson/django-debug-toolbar>`_
for Flask applications.

Usage
-----

Installing the debug toolbar is simple::

    from flask import Flask
    from flask_debugtoolbar import DebugToolbarExtension

    app = Flask(__name__)
    toolbar = DebugToolbarExtension(app)


The toolbar will automatically be injected into Jinja templates when debug mode is on::

    app.debug = True


Installation
------------

Installing is simple with pip::

    $ pip install flask-debugtoolbar

