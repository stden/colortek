#!/usr/bin/env python
import lib
from apps.catalog.models import Order
from grab import Grab
from django.conf import settings
from hashlib import md5
from django.core.urlresolvers import reverse

LOG_FILES=False

def make_key(*args):
    return md5("".join(args)).hexdigest()

def test_payment(order):
    amount = str(order.cost + order.deliver_cost)
    paymentid = '23'
    key = make_key(
        amount, order.client.email, paymentid, settings.DO_SECRET
    )
    url = settings.SITE_URL + reverse('catalog:order-payment-notification')
    print url
    post = {
        'amount': amount,
        'userid': order.client.email,
        'paymentid': paymentid,
        'orderid': order.pk,
        'key': key
    }
    g = Grab()
    g.setup(post=post)
    g.go(url)
    if LOG_FILES:
        open('log.xml', 'w').write(g.response.body)


if __name__ == '__main__':
    test_payment(Order.objects.get(id=27))
