# Configuration file for the Sphinx documentation builder.

import os
import sys
import django
from datetime import datetime

# -- Path setup --------------------------------------------------------------

# Add project root (two levels up from this file) to sys.path
# conf.py is in docs/source/, so we go up twice to reach project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "news_portal.settings")

# Setup Django
django.setup()

# -- Project information -----------------------------------------------------

project = "News Portal"
author = "Dian"
release = "1.0.0"
copyright = f"{datetime.now().year}, {author}"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",      # auto-generate docs from docstrings
    "sphinx.ext.viewcode",     # add links to highlighted source code
    "sphinx.ext.napoleon",     # support for Google/NumPy style docstrings
    "sphinx.ext.todo",         # support for TODOs
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = "alabaster"  # or 'sphinx_rtd_theme' if installed
html_static_path = ["_static"]

# -- Extension configuration -------------------------------------------------

# Napoleon settings (for Google/NumPy docstring style)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False

# Autodoc settings
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "private-members": False,
    "show-inheritance": True,
}

# TODO extension
todo_include_todos = True


