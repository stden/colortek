from django.conf.urls import patterns, include, url
from apps.core.shortcuts import direct_to_template

urlpatterns = patterns(
    'apps.catalog.views_json',
    url(r'containers/(?P<pk>\d+)/$', 'container', name='container'),
    url(r'containers/item/(?P<pk>\d+)/$', 'item', name='item'),
    url(r'service/(?P<pk>\d+)/orders/price', 'order_price', name='order-price'),
    url(r'orders/not/confirmed', 'orders_not_confirmed', name='orders-not-confirmed'),
)
