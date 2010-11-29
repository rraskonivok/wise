from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
     (r'^$', 'wise.worksheet.views.home'),
     (r'^home$', 'wise.worksheet.views.home'),
     (r'^users$', 'wise.worksheet.views.users'),
#     (r'^test$', 'wise.worksheet.views.test'),
     (r'^log$', 'wise.worksheet.views.log'),
     (r'^dict$', 'wise.worksheet.views.dict'),
     (r'^translate$', 'wise.worksheet.views.translate'),

     # REST API  uses django-piston
     (r'^api/', include('wise.api.urls')),

     # Heartbeat
     (r'^hb$', 'wise.worksheet.ajax.heartbeat'),

     # Authentication
     (r'^accounts/login/$', 'wise.worksheet.views.account_login'),
     (r'^accounts/logout/$', 'wise.worksheet.views.account_logout'),

     # Worksheet
     (r'^ws/(?P<eq_id>\d+)/$', 'wise.worksheet.views.ws'),
     (r'^palette/$', 'wise.worksheet.views.palette'),
     (r'^rule_request/$', 'wise.worksheet.ajax.rules_request'),
     (r'^new_workspace/$', 'wise.worksheet.views.new_workspace'),
     (r'^del_workspace/$', 'wise.worksheet.views.del_workspace'),

     # Worksheet Commands
     (r'^cmds/new_line/$', 'wise.worksheet.ajax.new_line'),
     (r'^cmds/new_cell/$', 'wise.worksheet.ajax.new_cell'),

     # Worksheet Math Actions
     (r'^cmds/apply_rule/$', 'wise.worksheet.ajax.apply_rule'),
     (r'^cmds/apply_def/$', 'wise.worksheet.ajax.apply_def'),
     (r'^cmds/apply_transform/$', 'wise.worksheet.ajax.apply_transform'),

     # Worksheet Command Line
     (r'^cmds/use_infix/$', 'wise.worksheet.ajax.use_infix'),

     # Uncomment the next line to enable the admin:
     (r'^admin/', include(admin.site.urls)),

     # Sphinx documentation
     (r'^docs/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'docs/_build/html','show_indexes': True}),


     # TODO: Firefox 4 has some issue with OpenType fonts being loaded 
     # from /static when the current page is /ws since it is one level 
     # up which violates it's same origin policy
     (r'^ws/mathjax/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT + '/mathjax'}),

     (r'^img/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT + '/img'}),
     (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT + '/admin'}),
     (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

