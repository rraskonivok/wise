from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from wise.api.auth import DjangoAuthentication

from wise.api.handlers import CellHandeler, ExpressionHandeler, \
WorkspaceHandeler, AssumptionHandeler

#TODO: add authentication on per user basis

django_auth = DjangoAuthentication(login_url='/accounts/login')

cells = Resource(handler=CellHandeler,
        authentication=django_auth)

exps = Resource(handler=ExpressionHandeler,
        authentication=django_auth)

asms = Resource(handler=AssumptionHandeler,
        authentication=django_auth)

workspaces = Resource(handler=WorkspaceHandeler,
        authentication=django_auth)

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

