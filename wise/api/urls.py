from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from wise.api.handlers import CellHandeler, ExpressionHandeler

#auth = HttpBasicAuthentication(realm='Wise API')
cells = Resource(handler=CellHandeler)
exps = Resource(handler=ExpressionHandeler)

urlpatterns = patterns('',

   # Cells
   url(r'^cell/(?P<id>[^/]+)/', cells, name='cells'),
   url(r'^cell/', cells),

   # Expressions
   url(r'^exp/(?P<id>[^/]+)/', exps, name='exps'),
   url(r'^exp/', exps),
)
