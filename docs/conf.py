# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath("../"))
print(f'Python path: {sys.path}')

project = 'PyAWG'
copyright = '2025, Abhishek Bawkar'
author = 'Abhishek Bawkar'
release = '0.3.7.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Show inherited members for classes
autodoc_default_options = {
    'members': True,
    'inherited-members': True,  # Explicitly include inherited members
    'show-inheritance': True,
    'exclude-members': '__weakref__'  # Optional: exclude specific members
}

autodoc_pydantic_model_show_validator_members = False
autoclass_content = "class"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_pdj_theme'
html_static_path = ['_static']
