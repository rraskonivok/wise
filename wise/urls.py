from random import randint

from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from django.contrib.auth.views import password_change
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.simple import direct_to_template, redirect_to

from worksheet.ajax import (
        socketio
)

def secure_class_view(regex, view, name=None):
    return url(
        regex,
        login_required(view.as_view()),
        name=name
    )

# Generic Class Views
from worksheet.views import (HomeView, WorksheetDelete,
        WorksheetEdit, WorksheetCreate)

admin.autodiscover()

urlpatterns = patterns('',

     url(
         r'^$',
         'django.views.generic.simple.redirect_to',
         {'url': settings.HOME_URL },
         name='index'
     ),

     url(r'^statichome/$',
         direct_to_template,
         {'template': 'statichome.html'},
         name='statichome'
     ),

     secure_class_view(
         r'^home$',
         HomeView,
         name='home'
     ),

     # REST API  uses django-piston
     (r'^api/', include('wise.api.urls')),

     #(r'^test$', 'wise.worksheet.views.test'),
     (r'dict/(?P<data>.*)$', 'wise.worksheet.views.internal_dict'),
     (r'^translate$', 'wise.worksheet.views.translate'),
     (r'graph/(?P<package>.*)$', 'wise.worksheet.views.objectgraph'),
     url(r'^ecosystem$',
         'wise.worksheet.views.ecosystem',
         name='ecosystem'
     ),

     url(r'^unit$',
         'wise.worksheet.views.unittest',
         name='unittest'
     ),

    # Socket IO hook
    url(
        regex=r'^socket\.io',
        view=socketio,
        name='socketio'
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
         secure_class_view(
            r'^ws/create/$',
            WorksheetCreate,
            name='worksheet_create'
         ),

         # READ
         (r'^ws/(?P<ws_id>\d+)/$', 'wise.worksheet.views.ws'),
         (r'^ws/(?P<ws_id>\d+)/export/(?P<format>.*)$', 'wise.worksheet.views.ws_export'),

         url(r'^ws/(?P<ws_id>\d+)/read$',
                 'wise.worksheet.views.ws_read',
                 name="worksheet_read"),

         # UPDATE
         secure_class_view(
            r'^ws/(?P<pk>\d+)/update/$',
            WorksheetEdit,
            name='worksheet_update'
         ),

         # DELETE
         secure_class_view(
             r'^ws/(?P<pk>\d+)/delete/$',
            WorksheetDelete,
            name='worksheet_delete'
         ),



     # Math Palettes
     (r'^palette/$', 'wise.worksheet.views.palette'),
     (r'^rule_request/$', 'wise.worksheet.ajax.rules_request'),

     # Worksheet Commands
     (r'^cmds/new_line/$', 'wise.worksheet.ajax.new_line'),
     (r'^cmds/new_cell/$', 'wise.worksheet.ajax.new_cell'),
     (r'^cmds/apply_rule/$', 'wise.worksheet.ajax.apply_rule'),
     (r'^cmds/apply_transform/$', 'wise.worksheet.ajax.apply_transform'),
     (r'^cmds/use_infix/$', 'wise.worksheet.ajax.use_infix'),
     (r'^cmds/draw_graph/$', 'wise.worksheet.ajax.use_infix'),

     # Uncomment the next line to enable the admin, append a
     # random integer on the end to obscure the url. Not really
     # more secure but it stops some automated bot attacks. Use
     # reverse("admin:index") to get the url inside of templates
     #url(r'^admin/%s' % randint(0,1e5), include(admin.site.urls))
     url(r'^admin/', include(admin.site.urls)),

     #(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to',
     #        {'url': '/static/img/favicon.ico'}),

     url(r'^experiment$',
         direct_to_template,
         {'template': 'experiment.html'},
         name='experiments'
     ),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^tests/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT + '/js/tests'}),
    )

     # Firefox 4 has some issue with OpenType fonts being loaded
     # from /media when the current page is /ws since it is one level
     # up which violates it's same origin policy
    urlpatterns += patterns('',
        (r'^fonts/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT + '/fonts'}),
    )

    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT + '/',
             'show_indexes': True
            }),
    )

    urlpatterns += patterns('',
        (r'^static/admin/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT + '/admin',
             'show_indexes': True
        }),
    )
else:
    # Static Files
    urlpatterns += staticfiles_urlpatterns()

# Grapelli Admin Interface
if 'grappelli' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^grappelli/', include('grappelli.urls')),
    )

# Django Sentry
if 'sentry' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
     url(r'^sentry/', include('sentry.urls'), name='sentry'),
    )
