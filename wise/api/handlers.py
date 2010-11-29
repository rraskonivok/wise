from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc, require_mime, require_extended

from django.core.exceptions import ObjectDoesNotExist
from wise.worksheet.models import Cell, Workspace, Expression, \
Assumption

class CellHandeler(BaseHandler):
    model = Cell
    fields = ()
    allowed_methods = ('GET', 'PUT', 'DELETE', 'POST')
    exclude = ('workspace')

    fields = ('index', 'id', ('workspace', ('id',)))

    # Example output:
    # {
    #     "index": 0, 
    #     "id": 1, 
    #     "workspace": {
    #         "id": 1, 
    #         "resource_uri": "/api/ws/1"
    #     }, 
    #     "resource_uri": "/api/cell/1"
    # }, 

    def read(self, request, id=None):
        cells = Cell.objects


        if id:
            try:
                return cells.get(id=id)
            except ObjectDoesNotExist:
                return rc.NOT_FOUND
        else:
            return cells.all()

    def create(self, request, id=None):
        request_data = self.flatten_dict(request.data)

        ws_id = request_data['workspace']
        index = request_data['index']

        ws = Workspace.objects.get(id=ws_id)
        em = Cell(workspace=ws,index=index)
        em.save()

        # Return the JSON of the new model for Backbone to inject
        # into the model
        return em

    def update(self, request, id=None):
        request_data = self.flatten_dict(request.data)

        cell_id = request_data['id']
        em = self.model.objects.get(id=cell_id)
        em.save()

        return em

    def delete(self, request, id=None):
        cell = Cell.objects.get(id=id)
        cell.delete()

        return rc.DELETED

    @classmethod
    def resource_uri(self):
        return ('cells', [ 'id', ])

class ExpressionHandeler(BaseHandler):
    model = Expression

    fields = ('index', 'sexp', 'annotation', ('cell', ('id',)))
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

        cell_id = request_data['cell']
        sexp = request_data['sexp']
        annotation = request_data['annotation']
        index = request_data['index']

        parent_cell = Cell.objects.get(id=cell_id)

        expr = Expression(cell=parent_cell,
                          sexp=sexp,
                          annotation=annotation,
                          index=index)
        expr.save()


        # Return the JSON of the new model for Backbone to inject
        # into the model
        return expr

    def update(self, request, id):
        request_data = self.flatten_dict(request.data)

        sexp = request_data['sexp']
        annotation = request_data['annotation']
        index = request_data['index']

        expr = Expression.objects.get(id=id)
        expr.sexp = sexp

        expr.save()

        # Return the JSON of the new model for Backbone to inject
        # into the model
        return expr

    @classmethod
    def resource_uri(self):
        return ('exps', [ 'id', ])

class AssumptionHandeler(BaseHandler):
    model = Assumption

    fields = ('index', 'sexp', 'annotation', ('cell', ('id',)))
    exclude = ()

    allowed_methods = ('GET', 'PUT', 'DELETE', 'POST')

    def read(self, request, id=None):
        exprs = Assumption.objects

        if id:
            try:
                return exprs.get(id=id)
            except ObjectDoesNotExist:
                return rc.NOT_FOUND
        else:
            return exprs.all()

    def create(self, request):
        request_data = self.flatten_dict(request.data)

        cell_id = request_data['cell']
        sexp = request_data['sexp']
        annotation = request_data['annotation']
        index = request_data['index']

        parent_cell = Cell.objects.get(id=cell_id)

        expr = Assumption(cell=parent_cell,
                          sexp=sexp,
                          annotation=annotation,
                          index=index)
        expr.save()

        # Return the JSON of the new model for Backbone to inject
        # into the model
        return expr

    def update(self, request, id):
        request_data = self.flatten_dict(request.data)

        sexp = request_data['sexp']
        annotation = request_data['annotation']
        index = request_data['index']

        expr = Assumption.objects.get(id=id)
        expr.sexp = sexp

        expr.save()

        # Return the JSON of the new model for Backbone to inject
        # into the model
        return expr

    @classmethod
    def resource_uri(self):
        return ('asms', [ 'id', ])

class WorkspaceHandeler(BaseHandler):
    model = Workspace

    fields = ('name',
              'timestamp',
              'public',
                 ('owner', ( 'username',))
             )
    #exclude = ('owner')

    allowed_methods = ('GET', 'PUT', 'DELETE', 'POST')

    def read(self, request, id=None):
        wss = Workspace.objects

        if id:
            try:
                return wss.get(id=id)
            except ObjectDoesNotExist:
                return rc.NOT_FOUND
        else:
            return wss.all()

    def create(self, request):
        request_data = self.flatten_dict(request.data)

        # Return the JSON of the new model for Backbone to inject
        # into the model
        return None

    @classmethod
    def resource_uri(self):
        return ('workspaces', [ 'id', ])
