from django.conf.urls import patterns, include, url
from apps.core.shortcuts import direct_to_template

urlpatterns = patterns(
    'apps.geo.views_json',
    url(r'subways/(?P<city_pk>\d+)/$', 'subways', name='subways'),
)
