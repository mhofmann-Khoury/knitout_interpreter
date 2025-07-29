"""
Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
import os
import sys

# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document) are in another directory, add these
# directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

# Add the src directory to the Python path so Sphinx can find your modules
sys.path.insert(0, os.path.abspath('../../src'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'knitout-interpreter'
copyright = '2024, Northeastern University ACT Lab'  # noqa: A001
author = 'Megan Hofmann'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# Import version from your package
try:
    from knitout_interpreter import __version__

    version = __version__.split('+')[0]  # Remove any +dev suffix
    release = __version__
except ImportError:
    # Fallback version if package can't be imported
    __version__ = '0.0.17'
    version = '0.0.17'
    release = '0.0.17'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # Core Sphinx extensions for auto-documentation
    'sphinx.ext.autodoc',  # Automatically document from docstrings
    'sphinx.ext.autosummary',  # Generate summary tables
    'sphinx.ext.viewcode',  # Add links to source code
    'sphinx.ext.napoleon',  # Support Google/NumPy style docstrings
    'sphinx.ext.intersphinx',  # Link to other project's documentation
    'sphinx.ext.todo',  # Support for todo items
    'sphinx.ext.coverage',  # Coverage checker for documentation
    'sphinx.ext.ifconfig',  # Conditional content

    # Additional extensions you have installed
    'sphinx_rtd_theme',  # Read the Docs theme
    'myst_parser',  # Markdown support
    'sphinx_autodoc_typehints',  # Better type hint support
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The suffix(es) of source filenames.
source_suffix = {
    '.rst': None,
    '.md': 'myst_parser',
}

# The master toctree document.
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# The theme to use for HTML and HTML Help pages.
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
html_theme_options = {
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom CSS files
html_css_files = [
    'custom.css',  # We'll create this for custom styling
]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Extension configuration -------------------------------------------------

# -- Options for autodoc extension ------------------------------------------
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Don't skip __init__ methods
autodoc_default_flags = ['members']

# -- Options for autosummary extension --------------------------------------
autosummary_generate = True
autosummary_imported_members = True

# -- Options for napoleon extension -----------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for intersphinx extension --------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'virtual_knitting_machine': ('https://virtual-knitting-machine.readthedocs.io/en/latest/', None),
    'knit_graphs': ('https://knit-graphs.readthedocs.io/en/latest/', None),
}

# -- Options for todo extension ---------------------------------------------
todo_include_todos = True

# -- Options for MyST parser ------------------------------------------------
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

# -- Custom configuration ---------------------------------------------------

# Add custom roles for highlighting
rst_prolog = """
.. role:: python(code)
   :language: python
   :class: highlight

.. role:: knitout(code)
   :language: text
   :class: highlight
"""

# Project URLs for the sidebar
html_context = {
    "display_github": True,
    "github_user": "mhofmann-Khoury",
    "github_repo": "knitout_interpreter",
    "github_version": "main",
    "conf_py_path": "/docs/source/",
}

# Logo and favicon
html_logo = "_static/logo.png"  # Add your logo if you have one
html_favicon = "_static/favicon.ico"  # Add favicon if you have one

# Add version info to the sidebar
html_title = f"{project} v{version}"

# Show "Edit on GitHub" links
html_show_sourcelink = True

# Add last updated timestamp
html_last_updated_fmt = '%b %d, %Y'

# -- Type hints configuration -----------------------------------------------
# Always document parameter types
always_document_param_types = True

# Simplify type hints
simplify_optional_unions = True

# -- API documentation configuration ----------------------------------------
# Automatically generate API documentation
autoapi_dirs = ['../../src/knitout_interpreter']
autoapi_root = 'api'
autoapi_add_toctree_entry = False
