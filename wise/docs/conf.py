# -*- coding: utf-8 -*-

import sys, os

this = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.pardir, os.pardir))
sys.path.append(os.path.join(this, os.pardir))

import wise
from wise import settings

from django.core.management import setup_environ
from django.template import loader
setup_environ(settings)

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.pngmath']

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'Wise'
copyright = u'2011, Stephen Diehl'

version = '0.1.0'
release = '0.1.0'

exclude_patterns = ['_build']

pygments_style = 'sphinx'

html_theme = 'nature'

html_static_path = ['_static']

html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
html_use_smartypants = True

htmlhelp_basename = 'Wisedoc'

# -- Options for LaTeX output --------------------------------------------------

# The paper size ('letter' or 'a4').
#latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
#latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'Wise.tex', u'Wise Documentation',
   u'Stephen Diehl', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Additional stuff for the LaTeX preamble.
#latex_preamble = ''

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'wise', u'Wise Documentation',
     [u'Stephen Diehl'], 1)
]

# If true, show URL addresses after external links.
#man_show_urls = False

# -- Options for Texinfo output ------------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  ('index', 'Wise', u'Wise Documentation', u'Stephen Diehl',
   'Wise', 'One line description of project.', 'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
texinfo_appendices = []
