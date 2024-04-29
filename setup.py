from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="Flask-DebugToolbar",
    install_requires=[
        'Flask>=2.3.0',
        'itsdangerous',
        'werkzeug',
        'MarkupSafe',
        'packaging',
    ],
     extras_require={
        "docs": [
            'Sphinx>=1.2.2',
            'Pallets-Sphinx-Themes',
        ],
     }
)
