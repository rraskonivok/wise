from django import template

import worksheet.exceptions as exception
from worksheet.utils import load_haml_template

class Cell(object):
    html = load_haml_template('cell.tpl')

    index = None
    id = None
    sid = None
    css_class = None

    def __init__(self, eqs, asms, **kwargs):
        self.expressions = eqs
        self.assumptions = asms
        self.__dict__.update(kwargs)

    def _pure_(self):
        # This is not defeind explicityly for the reason that inheriting
        # the method to generate a Pure object will often result in very
        # unexpected consequences if you not well thought out. Just define
        # one for every object
        raise exception.PureError('No Pure representation of %s.' % self.classname)

    def _latex_(self):
        raise Exception('No LaTeX representation of %s.' % self.classname)

    def _sage_(self):
        raise Exception('No Sage representation of %s.' % self.classname)

    def get_html(self):
        c = template.Context({
            'id': self.id,
            'index': self.index,
            'sid': self.sid,
            'expressions': [eq.get_html() for eq in self.expressions],
            'assumptions': [asm.get_html() for asm in self.assumptions],
            'class': self.css_class,
            })

        return self.html.render(c)

    def json_flat(self,lst=None):
        if not lst:
            lst = []

        if self.sid:
            resource_uri = '/api/cell/' + str(self.sid)
        else:
            resource_uri = None

        lst.append({'index': self.index,
                    'id' : self.id,
                    'sid': self.sid,
                    'resource_uri': resource_uri,
                    'eqs': [eq.id for eq in self.expressions]
                    })

        lst.append([eq.json_flat() for eq in self.expressions])
        lst.append([asm.json_flat() for asm in self.assumptions])

        return lst
