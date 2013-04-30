from django.conf.urls import patterns, include, url
from apps.core.shortcuts import direct_to_template

urlpatterns = patterns(
    'apps.accounts.views_json',
    url(r'profile/phones/$', 'phones', name='phones'),
    url(r'profile/phones/types/$', 'phone_types', name='phone-types'),
)
