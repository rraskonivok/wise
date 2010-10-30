from django.conf.urls.defaults import *

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
     (r'^$', 'wise.worksheet.views.home'),
     (r'^home$', 'wise.worksheet.views.home'),
     (r'^users$', 'wise.worksheet.views.users'),
#     (r'^test$', 'wise.worksheet.views.test'),
     (r'^log$', 'wise.worksheet.views.log'),
     (r'^translate$', 'wise.worksheet.views.translate'),
     (r'^hb$', 'wise.worksheet.ajax.heartbeat'),

     #Authentication
     (r'^accounts/login/$', 'wise.worksheet.views.account_login'),
     (r'^accounts/logout/$', 'wise.worksheet.views.account_logout'),

     #Worksheet
     (r'^ws/(?P<eq_id>\d+)/$', 'wise.worksheet.views.ws'),
     (r'^ws/(?P<eq_id>\d+)/save/$', 'wise.worksheet.ajax.save_workspace'),
     (r'^palette/$', 'wise.worksheet.views.palette'),
     (r'^new_workspace/$', 'wise.worksheet.views.new_workspace'),
     (r'^del_workspace/$', 'wise.worksheet.views.del_workspace'),

     #Worksheet Commands
     (r'^cmds/new_line/$', 'wise.worksheet.ajax.new_line'),
     (r'^cmds/receive/$', 'wise.worksheet.ajax.receive'),
     (r'^cmds/remove/$', 'wise.worksheet.ajax.remove'),

     #Transformations
     (r'^cmds/apply_rule/$', 'wise.worksheet.ajax.apply_rule'),
     (r'^cmds/apply_def/$', 'wise.worksheet.ajax.apply_def'),
     (r'^cmds/apply_transform/$', 'wise.worksheet.ajax.apply_transform'),
     (r'^cmds/pure_parse/$', 'wise.worksheet.ajax.pure_parse'),
     (r'^cmds/use_infix/$', 'wise.worksheet.ajax.use_infix'),

     #Rules
     (r'^rule/$', 'wise.worksheet.views.rules_list'),
     (r'^rule/(?P<rule_id>\d+)/$', 'wise.worksheet.views.rule'),
     (r'^rule/(?P<rule_id>\d+)/save/$', 'wise.worksheet.ajax.save_ruleset'),
     (r'^rule_request/$', 'wise.worksheet.ajax.rules_request'),

     #Uncomment the next line to enable the admin:
     (r'^admin/', include(admin.site.urls)),
     (r'^docs/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'docs/_build/html','show_indexes': True}),
)

from django.conf import settings

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
