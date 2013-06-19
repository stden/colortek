# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from cart import Cart
from django.conf import settings
from apps.catalog.models import Item, Addon, Service, Order, Vote
from apps.core.helpers import get_model_content_type
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal


def cart(request):
    _cart = Cart(request)
    items = len(list(_cart.cart.item_set.all()))
    item_ct = get_model_content_type(Item)
    addon_ct = get_model_content_type(Addon)

    products = _cart.cart.item_set.filter(content_type=item_ct)
    addons = _cart.cart.item_set.filter(content_type=addon_ct)
    total_price = _cart.get_total_price()
    bonus_max = round(
        total_price * Decimal(str(0.1 / settings.DEFAULT_EXCHANGE_RATE))
    )
    service = None
    deliver_cost = None

    if products:
        # item could be deleted so careful
        try:
            service = products.all()[0].product.container.owner
            deliver_cost = service.get_deliver_cost(total_price)
        except ObjectDoesNotExist:
            _cart.cart.item_set.all().delete()
    context = {
        'cart': _cart,
        'kart': {
            'total_price': _cart.get_total_price(),
            'products': products,
            'cart_items': items or None,
            'addons': addons,
            'bonus_max': int(bonus_max),
            'service': service,
            'deliver_cost': int(deliver_cost) if deliver_cost is not None else None
        }
    }

    return context


def services(request):
    return {
        'servs': Service.objects.all()
    }

def stats(request):
    now = datetime.now()
    today = datetime(year=now.year, month=now.month, day=now.day)
    end_today = today + timedelta(hours=23, minutes=59, seconds=59)
    today_orders_count = Order.objects.filter(
        created_on__gte=today, created_on__lte=end_today
    ).count()
    return {
        'today_orders_count': today_orders_count
    }

def votes(request):
    if request.user.is_authenticated():
        offset = datetime.now() + timedelta(hours=24)
        votes = Vote.objects.filter(
            client=request.user,
            is_proceeded=False,
            updated_on__lte=offset
        )
        return {'active_votes': votes}
    return {}
