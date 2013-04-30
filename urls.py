from django.conf.urls import patterns, include, url
from django.conf import settings
from filebrowser.sites import site

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from apps.core.shortcuts import direct_to_template
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'template.views.home', name='home'),
    # url(r'^template/', include('template.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^$', 'apps.catalog.views.index', name='index'),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('apps.core.urls', namespace='core')),
    url(r'^', include('apps.accounts.urls', namespace='accounts')),
    url(r'^catalog/', include('apps.catalog.urls', namespace='catalog')),
    url(r'^blog/', include('apps.blog.urls', namespace='blog')),
    url(r'^geo/', include('apps.geo.urls', namespace='geo')),
    url(r'^json/', include('apps.jsonapp.urls', namespace='json')),
    url(r'^splash/$', direct_to_template,
        kwargs=dict(template='splash.html'))

)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT ,
            'show_indexes': True,
            }
        )
    )

urlpatterns += patterns('',
    url(r'^', include('apps.pages.urls')),
)
