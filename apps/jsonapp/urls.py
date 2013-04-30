from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'template.views.home', name='home'),
    # url(r'^template/', include('template.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^accounts/', include('apps.accounts.urls_json', namespace='accounts')),
    url(r'^catalog/', include('apps.catalog.urls_json', namespace='catalog')),
    url(r'^geo/', include('apps.geo.urls_json', namespace='geo')),

)
