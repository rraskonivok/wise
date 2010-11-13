from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc, require_mime, require_extended

from django.core.exceptions import ObjectDoesNotExist
from wise.worksheet.models import Cell, Workspace, Expression

class CellHandeler(BaseHandler):
    model = Cell
    fields = ()
    allowed_methods = ('GET', 'PUT', 'DELETE', 'POST')
    exclude = ('workspace')

    def read(self, request, id=None):
        cells = Cell.objects


        if id:
            try:
                return cells.get(id=id)
            except ObjectDoesNotExist:
                return rc.NOT_FOUND
        else:
            return cells.all()

    def create(self, request):
        request_data = self.flatten_dict(request.data)

        ws_id = request_data['ws']
        #index = request_data['index']

        ws = Workspace.objects.get(id=ws_id)
        em = self.model(workspace=ws,index=1)
        em.save()

        # Return the JSON of the new model for Backbone to inject
        # into the model
        return em

    @classmethod
    def resource_uri(self):
        return ('cells', [ 'id', ])

class ExpressionHandeler(BaseHandler):
    model = Expression

    fields = ()
    exclude = ()

    allowed_methods = ('GET', 'PUT', 'DELETE', 'POST')

    def read(self, request, id=None):
        exprs = Expression.objects


        if id:
            try:
                return exprs.get(id=id)
            except ObjectDoesNotExist:
                return rc.NOT_FOUND
        else:
            return exprs.all()

    def create(self, request):
        request_data = self.flatten_dict(request.data)

        #cell_id = request_data['cell']
        #index = request_data['index']

        ws = Workspace.objects.get(id=cell_id)
        #em = self.model(workspace=ws,index=1)
        #em.save()

        # Return the JSON of the new model for Backbone to inject
        # into the model
        return None

    @classmethod
    def resource_uri(self):
        return ('exps', [ 'id', ])
