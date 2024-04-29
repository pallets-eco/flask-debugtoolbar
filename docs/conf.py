import importlib.metadata

# Project --------------------------------------------------------------

project = "Flask-DebugToolbar"
version = release = importlib.metadata.version("flask-debugtoolbar").partition(".dev")[
    0
]

# General --------------------------------------------------------------

default_role = "code"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.log_cabinet",
    "pallets_sphinx_themes",
]
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_preserve_defaults = True
extlinks = {
    "issue": ("https://github.com/pallets-eco/flask-debugtoolbar/issues/%s", "#%s"),
    "pr": ("https://github.com/pallets-eco/flask-debugtoolbar/pull/%s", "#%s"),
}
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "flasksqlalchemy": ("https://flask-sqlalchemy.palletsprojects.com", None),
}

# HTML -----------------------------------------------------------------

html_theme = "flask"
html_static_path = ["_static"]
html_copy_source = False
html_show_copyright = False
html_use_index = False
html_domain_indices = False
