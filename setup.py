from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="Flask-DebugToolbar",
    install_requires=[
        'Flask>=0.8',
        'Blinker',
        'itsdangerous',
        'werkzeug',
    ],
)
