from django.conf.urls import patterns, include, url
from apps.core.shortcuts import direct_to_template

urlpatterns = patterns(
    'apps.geo.views',
    url(r'city/(?P<city_pk>\d+)/set/$', 'city_set', name='city-set'),
    url(r'city/(?P<city_pk>\d+)/subway/widget/$',
        'subway_widget', name='subway-widget'),
    url(r'position/(?P<pk>\d+)/delete/$', 'position_delete',
        name='position-delete'),
)
