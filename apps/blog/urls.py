from django.conf.urls import patterns, include, url
from apps.core.shortcuts import direct_to_template

urlpatterns = patterns(
    'apps.blog.views',
    url(r'^$', 'index', name='index'),
    url(r'category/(?P<pk>\d+)/$', 'category', name='category'),
    url(r'search/$', 'search', name='search'),
    url(r'^(?P<pk>\d+)/$', 'post', name='post'),
)
