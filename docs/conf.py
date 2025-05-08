
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
project = 'Limelight FTC Bridge'
copyright = '2025, Nadege Lemperiere'
author = 'Nadege Lemperiere'

# -- General configuration ---------------------------------------------------
extensions = []

templates_path = ['_templates']
exclude_patterns = []
github_url = 'https://github.com/nadegelemperiere-robotics/limenurse'

# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'
html_static_path = ['_static']
html_theme = 'sphinx_rtd_theme'
html_logo = '_static/logo.png'
html_favicon = '_static/favicon.ico'
html_theme_options = {
    'logo_only': True,
    'display_version': False,
}
html_context = {
    'display_github': True,
    'github_repo': 'nadegelemperiere-robotics/limenurse'
}