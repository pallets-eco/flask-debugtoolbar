.. Flask-DebugToolbar documentation master file, created by
   sphinx-quickstart on Wed Feb 15 18:08:39 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Flask-DebugToolbar's documentation!
==============================================

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


Configuration
-------------

The toolbar support several configuration options:

================================  =====================================   ==========================
Name                              Description                             Default
================================  =====================================   ==========================
``DEBUG_TB_ENABLED``              Enable the toolbar?                     ``app.debug``
``DEBUG_TB_HOSTS``                Whitelist of hosts to display toolbar   any host
``DEBUG_TB_INTERCEPT_REDIRECTS``  Should intercept redirects?             ``True``
``DEBUG_TB_PANELS``               List of module/class names of panels    enable all built-in panels
================================  =====================================   ==========================

To change one of the config options, set it in the Flask app's config like::

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


Contributing
------------

Fork us `on GitHub <https://github.com/mgood/flask-debugtoolbar>`_


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

