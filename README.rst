Flask Debug-toolbar
===================

This is a port of the excellent `django-debug-toolbar <https://github.com/django-debug-toolbar/django-debug-toolbar>`_
for Flask applications.


Installation
------------

Installing is simple with pip::

    $ pip install flask-debugtoolbar


Usage
-----

Setting up the debug toolbar is simple::

    from flask import Flask
    from flask_debugtoolbar import DebugToolbarExtension

    app = Flask(__name__)

    # the toolbar is only enabled in debug mode:
    app.debug = True

    # set a 'SECRET_KEY' to enable the Flask session cookies
    app.config['SECRET_KEY'] = '<replace with a secret key>'

    toolbar = DebugToolbarExtension(app)


The toolbar will automatically be injected into Jinja templates when debug mode is on.
In production, setting ``app.debug = False`` will disable the toolbar.

See the `documentation`_ for more information.

.. _documentation: http://flask-debugtoolbar.readthedocs.org
