from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc, require_mime, require_extended

from wise.worksheet.models import Cell

class CellHandeler(BaseHandler):
    model = Cell
    fields = ('id', 'workspace', 'index') 

    def read(self, request, id=None):
        base = Cell.objects

        if id:
            return base.get(id=id)
        else:
            return base.all()

    @classmethod
    def resource_uri(self):
        return ('cells', [ 'id', ])
