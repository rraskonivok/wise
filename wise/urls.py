from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
     (r'^$', 'wise.worksheet.views.home'),
     (r'^home$', 'wise.worksheet.views.home'),
     (r'^test$', 'wise.worksheet.views.test'),
     (r'^ws/(?P<eq_id>\d+)/$', 'wise.worksheet.views.eq'),
     (r'^palette/$', 'wise.worksheet.views.palette'),
     (r'^ws/(?P<eq_id>\d+)/check/$', 'wise.worksheet.views.check'),
     (r'^ws/(?P<eq_id>\d+)/term/$', 'wise.worksheet.views.term'),
     (r'^ws/(?P<eq_id>\d+)/apply/$', 'wise.worksheet.views.apply'),
     (r'^ws/(?P<eq_id>\d+)/receive/$', 'wise.worksheet.views.receive'),
     (r'^ws/(?P<eq_id>\d+)/remove/$', 'wise.worksheet.views.remove'),
     (r'^ws/(?P<eq_id>\d+)/down/$', 'wise.worksheet.views.down'),
     (r'^ws/(?P<eq_id>\d+)/topdown/$', 'wise.worksheet.views.topdown'),
     (r'^ws/(?P<eq_id>\d+)/action/$', 'wise.worksheet.views.action'),
     (r'^ws/(?P<eq_id>\d+)/propogate/$', 'wise.worksheet.views.propogate'),
     (r'^ws/(?P<eq_id>\d+)/lookup_transform/$', 'wise.worksheet.views.lookup_transform'),
     (r'^ws/(?P<eq_id>\d+)/apply_transform/$', 'wise.worksheet.views.apply_transform'),
     (r'^ws/(?P<eq_id>\d+)/lookup_identity/$', 'wise.worksheet.views.lookup_identity'),
     (r'^ws/(?P<eq_id>\d+)/apply_identity/$', 'wise.worksheet.views.apply_identity'),
     (r'^ws/(?P<eq_id>\d+)/save_workspace/$', 'wise.worksheet.views.save_workspace'),
     (r'^new_workspace/$', 'wise.worksheet.views.new_workspace'),
     (r'^del_workspace/$', 'wise.worksheet.views.del_workspace'),
     (r'^ws/(?P<eq_id>\d+)/combine/$', 'wise.worksheet.views.combine'),
     (r'^new/$', 'wise.worksheet.views.new'),

     #Uncomment the next line to enable the admin:
     (r'^admin/', include(admin.site.urls)),
)

from django.conf import settings

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
