from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
     #(r'^$', 'wise.worksheet.views.home'),
     (r'^home$', 'wise.worksheet.views.home'),
     (r'^test$', 'wise.worksheet.views.test'),

     #Authentication
     (r'^accounts/login/$', 'wise.worksheet.views.account_login'),
     (r'^accounts/logout/$', 'wise.worksheet.views.account_logout'),

     #Worksheet
     (r'^ws/(?P<eq_id>\d+)/$', 'wise.worksheet.views.ws'),
     (r'^palette/$', 'wise.worksheet.views.palette'),
     (r'^ws/(?P<eq_id>\d+)/receive/$', 'wise.worksheet.views.receive'),
     (r'^ws/(?P<eq_id>\d+)/remove/$', 'wise.worksheet.views.remove'),
     (r'^ws/(?P<eq_id>\d+)/lookup_transform/$', 'wise.worksheet.views.lookup_transform'),
     (r'^ws/(?P<eq_id>\d+)/apply_transform/$', 'wise.worksheet.views.apply_transform'),
     (r'^ws/(?P<eq_id>\d+)/save_workspace/$', 'wise.worksheet.views.save_workspace'),
     (r'^ws/(?P<eq_id>\d+)/sage_parse/$', 'wise.worksheet.views.sage_parse'),
     (r'^ws/(?P<eq_id>\d+)/sage_inline/$', 'wise.worksheet.views.sage_inline'),
     (r'^ws/(?P<eq_id>\d+)/new_inline/$', 'wise.worksheet.views.new_inline'),
     (r'^ws/(?P<eq_id>\d+)/json_tree/$', 'wise.worksheet.views.json_tree'),
     (r'^new_workspace/$', 'wise.worksheet.views.new_workspace'),
     (r'^del_workspace/$', 'wise.worksheet.views.del_workspace'),
     (r'^ws/(?P<eq_id>\d+)/combine/$', 'wise.worksheet.views.combine'),
     (r'^new/$', 'wise.worksheet.views.new'),

     #Symbols
     (r'^sym/$', 'wise.worksheet.views.symbols_list'),
     (r'^sym/(?P<sym_id>\d+)/$', 'wise.worksheet.views.sym'),
     (r'^sym/(?P<sym_id>\d+)/update/$', 'wise.worksheet.views.sym_update'),
     (r'^symbol_request/$', 'wise.worksheet.views.symbols_request'),

     #Symbols
     (r'^fun/$', 'wise.worksheet.views.fun_list'),
     (r'^fun/(?P<sym_id>\d+)/$', 'wise.worksheet.views.fun'),
     (r'^fun/(?P<sym_id>\d+)/update/$', 'wise.worksheet.views.sym_update'),
     (r'^functions_request/$', 'wise.worksheet.views.functions_request'),
     (r'^preview_function/$', 'wise.worksheet.views.preview_function'),

     #Uncomment the next line to enable the admin:
     (r'^admin/', include(admin.site.urls)),

)

from django.conf import settings

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
