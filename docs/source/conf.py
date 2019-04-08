import os
import sys

project = 'qAuth'
copyright = '2019, Ravisankar A V'
author = 'Ravisankar A V'
version = '0.0.1'
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
pygments_style = 'sphinx'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

sys.path.insert(0, os.path.abspath('../..'))
extensions = ['sphinx.ext.autodoc',]