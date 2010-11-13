from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from wise.api.handlers import CellHandeler, ExpressionHandeler, WorkspaceHandeler

auth = HttpBasicAuthentication(realm='Wise API')
cells = Resource(handler=CellHandeler)
exps = Resource(handler=ExpressionHandeler)
workspaces = Resource(handler=WorkspaceHandeler)

urlpatterns = patterns('',

   # Cells
   url(r'^cell/(?P<id>[^/]+)/', cells, name='cells'),
   url(r'^cell/', cells),

   # Expressions
   url(r'^exp/(?P<id>[^/]+)/', exps, name='exps'),
   url(r'^exp/', exps),

   # Expressions
   url(r'^ws/(?P<id>[^/]+)/', workspaces, name='workspaces'),
   url(r'^ws/', workspaces),
)