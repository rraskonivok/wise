from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
from django.conf import settings
from django.contrib.auth.views import password_change

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

from worksheet.views import (HomeView, WorksheetEdit,
WorksheetDetail, WorksheetDelete)

urlpatterns = patterns('',
     #url(r'^$', 'wise.worksheet.views.home', name='index'),
     #url(r'^$', 'wise.worksheet.views.HomeView',name='index'),

     url(r'^$', HomeView.as_view(), name='index'),
     url(r'^home$', HomeView.as_view(), name='home'),

     url(r'^ecosystem$', 'wise.worksheet.views.ecosystem', name='ecosystem'),
     # REST API  uses django-piston
     (r'^api/', include('wise.api.urls')),

#     (r'^test$', 'wise.worksheet.views.test'),
     (r'dict/(?P<data>.*)$', 'wise.worksheet.views.dict'),
     (r'^translate$', 'wise.worksheet.views.translate'),

     # Heartbeat
     (r'^hb$', 'wise.worksheet.ajax.heartbeat'),

     # Authentication
     (r'^accounts/', include('registration.backends.default.urls')),
     (r'^invite/', include('privatebeta.urls')),
     (r'^/accounts/password/change/$', password_change,
         {'template_name': 'registration/password_reset_form.html'}),

     url(r'^accounts/profile/$', direct_to_template,
         {'template': 'registration/profile.html'}, name='profile'),

     # Worksheet
     (r'^ws/(?P<ws_id>\d+)/$', 'wise.worksheet.views.ws'),
     (r'^palette/$', 'wise.worksheet.views.palette'),
     (r'^rule_request/$', 'wise.worksheet.ajax.rules_request'),

     # Worksheet CRUD
     #(r'^worksheet_delete/(?P<ws_id>\d+)/$', 'wise.worksheet.views.worksheet_delete'),
     #(r'^worksheet_edit/(?P<ws_id>\d+)/$', 'wise.worksheet.views.worksheet_edit'),
     #(r'^worksheet_edit/$', 'wise.worksheet.views.worksheet_edit'),
     #url(r'^worksheet_edit/(?P<ws_id>\d+)/$', WorksheetEdit.as_view()),

     url(r'^ws/detail/(?P<pk>\d+)/update/$',
        WorksheetEdit.as_view(),
        name='worksheet_update'),

     url(r'^ws/detail/(?P<pk>\d+)/delete/$',
        WorksheetDelete.as_view(),
        name='worksheet_delete'),

     url(r'^ws/detail/(?P<pk>\d+)/$',
        WorksheetDetail.as_view(),
        name='worksheet_detail'),

     #url(r'^worksheet_edit/', WorksheetEdit.as_view(),
     #    'worksheet_detail'),

     # Worksheet Commands
     (r'^cmds/new_line/$', 'wise.worksheet.ajax.new_line'),
     (r'^cmds/new_cell/$', 'wise.worksheet.ajax.new_cell'),
     (r'^cmds/apply_rule/$', 'wise.worksheet.ajax.apply_rule'),
     (r'^cmds/apply_def/$', 'wise.worksheet.ajax.apply_def'),
     (r'^cmds/apply_transform/$', 'wise.worksheet.ajax.apply_transform'),
     (r'^cmds/use_infix/$', 'wise.worksheet.ajax.use_infix'),

     # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls), name='admin'),

     # Sphinx documentation
#     url(r'^docs/(?P<path>.*)$', 'django.views.static.serve',
#         {'document_root': 'docs/_build/html','show_indexes': True},
#         name='docs'),

     # TODO: Firefox 4 has some issue with OpenType fonts being loaded
     # from /static when the current page is /ws since it is one level
     # up which violates it's same origin policy
#     (r'^ws/mathjax/(?P<path>.*)$', 'django.views.static.serve',
#             {'document_root': settings.MEDIA_ROOT + '/mathjax'}),
#
#     (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', 
#             {'url': '/static/img/favicon.ico'}),
)

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^tests/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.MEDIA_ROOT + '/js/tests'}),
    )


if 'grappelli' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^grappelli/', include('grappelli.urls')),
    )

if 'sentry' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
     url(r'^sentry/', include('sentry.urls'), name='sentry'),
    )
