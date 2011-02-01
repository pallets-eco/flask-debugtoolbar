from flask import Module

__all__ = ['views_module']

mod = views_module = Module(__name__)

@mod.endpoint('_debug_toolbar.example')
def example_view():
    return "example"
