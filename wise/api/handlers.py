from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc, require_mime, require_extended

from django.core.exceptions import ObjectDoesNotExist

from wise.worksheet.models import Cell, Workspace

from django.utils import simplejson as json

from worksheet.utils import JsonResponse

class CellHandeler(BaseHandler):
    model = Cell
    fields = ()
    allowed_methods = ('GET', 'PUT', 'DELETE', 'POST')
    exclude = ('workspace')

    def read(self, request, id=None):
        base = Cell.objects


        if id:
            try:
                return base.get(id=id)
            except ObjectDoesNotExist:
                return rc.NOT_FOUND
        else:
            return base.all()

    def create(self, request):
        request_data = self.flatten_dict(request.data)

        ws_id = request_data['ws']
        #index = request_data['index']

        ws = Workspace.objects.get(id=1)
        em = self.model(workspace=ws,index=1)
        em.save()

        # Return the JSON of the new model for Backbone to inject
        # into the model
        return em

    def update(self, request):
        print 'put request'
        resp = rc.CREATED
        return resp

    @classmethod
    def resource_uri(self):
        return ('cells', [ 'id', ])
