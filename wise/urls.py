from django.conf.urls.defaults import *

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
     (r'^$', 'wise.worksheet.views.home'),
     (r'^home$', 'wise.worksheet.views.home'),
     (r'^test$', 'wise.worksheet.views.test'),
     (r'^log$', 'wise.worksheet.views.log'),

     #Authentication
     (r'^accounts/login/$', 'wise.worksheet.views.account_login'),
     (r'^accounts/logout/$', 'wise.worksheet.views.account_logout'),

     #Worksheet
     (r'^ws/(?P<eq_id>\d+)/$', 'wise.worksheet.views.ws'),
     (r'^ws/(?P<eq_id>\d+)/save/$', 'wise.worksheet.views.save_workspace'),
     (r'^palette/$', 'wise.worksheet.views.palette'),
     (r'^new_workspace/$', 'wise.worksheet.views.new_workspace'),
     (r'^del_workspace/$', 'wise.worksheet.views.del_workspace'),

     #Worksheet Commands
     (r'^cmds/new_line/$', 'wise.worksheet.ajax.new_line'),
     (r'^cmds/receive/$', 'wise.worksheet.ajax.receive'),
     (r'^cmds/remove/$', 'wise.worksheet.ajax.remove'),
     (r'^cmds/lookup_transform/$', 'wise.worksheet.ajax.lookup_transform'),
     (r'^cmds/apply_rule/$', 'wise.worksheet.ajax.apply_rule'),
     (r'^cmds/apply_transform/$', 'wise.worksheet.ajax.apply_transform'),
     (r'^cmds/pure_parse/$', 'wise.worksheet.ajax.pure_parse'),
     (r'^cmds/json_tree/$', 'wise.worksheet.ajax.json_tree'),
     (r'^cmds/combine/$', 'wise.worksheet.ajax.combine'),

     #Rules
     (r'^rule/$', 'wise.worksheet.views.rules_list'),
     (r'^rule/(?P<rule_id>\d+)/$', 'wise.worksheet.views.rule'),
     (r'^rule/(?P<rule_id>\d+)/save/$', 'wise.worksheet.views.save_ruleset'),
     (r'^rule/new/$', 'wise.worksheet.views.sym_update'),
     (r'^rule_request/$', 'wise.worksheet.views.rules_request'),

     #Symbols
     (r'^sym/$', 'wise.worksheet.views.symbols_list'),
     (r'^sym/(?P<sym_id>\d+)/$', 'wise.worksheet.views.sym'),
     (r'^sym/new/$', 'wise.worksheet.views.sym_update'),
     (r'^symbol_request/$', 'wise.worksheet.views.symbols_request'),

     #Functions
     (r'^fun/$', 'wise.worksheet.views.fun_list'),
     (r'^fun/(?P<sym_id>\d+)/$', 'wise.worksheet.views.fun'),
     (r'^fun/new/$', 'wise.worksheet.views.fun_update'),
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
