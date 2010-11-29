from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from wise.api.handlers import CellHandeler, ExpressionHandeler, \
WorkspaceHandeler, AssumptionHandeler

#TODO: add authentication on per user basis

auth = HttpBasicAuthentication(realm='Wise API')
cells = Resource(handler=CellHandeler)
exps = Resource(handler=ExpressionHandeler)
asms = Resource(handler=AssumptionHandeler)
workspaces = Resource(handler=WorkspaceHandeler)

urlpatterns = patterns('',

   # Cells
   url(r'^cell/(?P<id>[^/]+)', cells, name='cells'),
   url(r'^cell/', cells),

   # Expressions
   url(r'^exp/(?P<id>[^/]+)', exps, name='exps'),
   url(r'^exp/', exps),

   # Assumptions
   url(r'^asm/(?P<id>[^/]+)', asms, name='asms'),
   url(r'^asm/', asms),

   # Expressions
   url(r'^ws/(?P<id>[^/]+)', workspaces, name='workspaces'),
   url(r'^ws/', workspaces),
)
