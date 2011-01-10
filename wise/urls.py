from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from django.contrib.auth.views import password_change
from django.contrib.auth.decorators import login_required as secure
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.simple import direct_to_template

# Generic Class Views
from worksheet.views import (HomeView, WorksheetDelete,
        WorksheetEdit, WorksheetCreate)

admin.autodiscover()

urlpatterns = patterns('',
     url(r'^$',
         secure(
             HomeView.as_view()
         ),
         name='index'
     ),

     url(r'^home$',
         secure(
             HomeView.as_view()
         ),
         name='home'
     ),


     # REST API  uses django-piston
     (r'^api/', include('wise.api.urls')),

     #(r'^test$', 'wise.worksheet.views.test'),
     (r'dict/(?P<data>.*)$', 'wise.worksheet.views.dict'),
     (r'^translate$', 'wise.worksheet.views.translate'),
     (r'graph/(?P<package>.*)$', 'wise.worksheet.views.objectgraph'),
     url(r'^ecosystem$',
         'wise.worksheet.views.ecosystem',
         name='ecosystem'
     ),

     # Heartbeat
     (r'^hb$', 'wise.worksheet.ajax.heartbeat'),

     # Authentication & User Profiles
     (r'^accounts/', include('registration.backends.default.urls')),
     (r'^invite/', include('privatebeta.urls')),
     url(r'^/accounts/password/change/$',
         password_change,
         {'template_name':
             'registration/password_reset_form.html'},
         name='password_change'
     ),
     url(r'^accounts/profile/$',
         direct_to_template,
         {'template': 'registration/profile.html'},
         name='profile'
     ),

     # Worksheet CRUD

         # CREATE
         url(r'^ws/create/$',
            secure(
                WorksheetCreate.as_view()
            ),
            name='worksheet_create'
         ),

         # READ
         (r'^ws/(?P<ws_id>\d+)/$', 'wise.worksheet.views.ws'),
         (r'^ws/(?P<ws_id>\d+)/read$', 'wise.worksheet.views.ws_read'),

         # UPDATE
         url(r'^ws/(?P<pk>\d+)/update/$',
            secure(
                WorksheetEdit.as_view()
            ),
            name='worksheet_update'
         ),

         # DELETE
         url(r'^ws/(?P<pk>\d+)/delete/$',
            secure(
                WorksheetDelete.as_view()
            ),
            name='worksheet_delete'
         ),

     # Math Palettes
     (r'^palette/$', 'wise.worksheet.views.palette'),
     (r'^rule_request/$', 'wise.worksheet.ajax.rules_request'),

     # Worksheet Commands
     (r'^cmds/new_line/$', 'wise.worksheet.ajax.new_line'),
     (r'^cmds/new_cell/$', 'wise.worksheet.ajax.new_cell'),
     (r'^cmds/apply_rule/$', 'wise.worksheet.ajax.apply_rule'),
     (r'^cmds/apply_def/$', 'wise.worksheet.ajax.apply_def'),
     (r'^cmds/apply_transform/$', 'wise.worksheet.ajax.apply_transform'),
     (r'^cmds/use_infix/$', 'wise.worksheet.ajax.use_infix'),
     (r'^cmds/draw_graph/$', 'wise.worksheet.ajax.use_infix'),

     # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls), name='admin'),

     # TODO: Firefox 4 has some issue with OpenType fonts being loaded
     # from /static when the current page is /ws since it is one level
     # up which violates it's same origin policy
     #(r'^ws/mathjax/(?P<path>.*)$', 'django.views.static.serve',
     #        {'document_root': settings.MEDIA_ROOT + '/mathjax'}),

     #(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', 
     #        {'url': '/static/img/favicon.ico'}),
)

# Static Files
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
