from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from wise.api.handlers import CellHandeler

auth = HttpBasicAuthentication(realm='Wise API')
cells = Resource(handler=CellHandeler, authentication=auth)

urlpatterns = patterns('',
   url(r'^cell/(?P<id>[^/]+)/', cells, name='cells'),
   url(r'^cells/', cells),
)
