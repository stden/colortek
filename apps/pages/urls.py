from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.pages.views',    
    url('(?P<url>.*)', 'page', name='page'),
)
