import worksheet.js as js
import worksheet.exceptions as exception
from worksheet.utils import load_haml_template

from django import template
from django.utils.safestring import SafeUnicode

class Cell(object):
    html = load_haml_template('cell.tpl')

    index = None
    id = None
    cid = None
    css_class = None

    def __init__(self, eqs):
        self.eqs = eqs

    def _pure_(self):
        # This is not defeind explicityly for the reason that inheriting
        # the method to generate a Pure object will often result in very
        # unexpected consequences if you not well thought out. Just define
        # one for every object
        raise exception.PureError('No Pure representation of %s.' % self.classname)

    def _latex_(self):
        raise exception.PureError('No LaTeX representation of %s.' % self.classname)

    def _sage_(self):
        raise exception.PureError('No Sage representation of %s.' % self.classname)

    def get_html(self):
        c = template.Context({
            'id': self.id,
            'index': self.index,
            'cid': self.cid,
            'eqs': [eq.get_html() for eq in self.eqs],
            'class': self.css_class,
            })

        return self.html.render(c)

    def json_flat(self,lst=None):
        if not lst:
            lst = []

        lst.append({'index': self.id,
                    #'assumptions': None,
                    'eqs': [eq.id for eq in self.eqs]})

        for term in self.eqs:
            term.json_flat(lst)

        return lst
