# -*- coding: utf-8 -*-
from cart import Cart
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from apps.catalog.models import Item, Addon
from apps.core.helpers import get_object_or_None, get_model_content_type
from django.contrib.contenttypes.models import ContentType
from django.db.models import get_model

from functools import partial


def not_empty_cart_required(func):
    def wrapper(request, *args, **kwargs):
        cart = Cart(request)
        if not cart.cart.item_set.count():
            return redirect('catalog:empty-cart')
        return func(request, *args, **kwargs)
    return wrapper


def operator_required(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_operator:
            return func(request, *args, **kwargs)
        return redirect('core:blockage')
    return wrapper


def check_provider_unique(field, type='item'):
    """
        checks if someone tries to add goods of the
        different delivery providers, if True than fail
    """
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            cart = Cart(request)
            pk = kwargs[field]
            if type == 'item':
                item = get_object_or_None(Item, pk=pk)
            elif type == 'addon':
                item = get_object_or_None(Addon, pk=pk)
            else:
                return func(request, *args, **kwargs)

            if not item:
                return func(request, *args, **kwargs)

            # always proceed if cart is clean
            if not cart.cart.item_set.count():
                return func(request, *args, **kwargs)
            item_ct = get_model_content_type(Item)
            addon_ct = get_model_content_type(Addon)

            if type == 'item':
                source_item = cart.cart.item_set.filter(
                    content_type=item_ct)[0]
                source_owner = source_item.product.container.owner
                dst_owner = item.container.owner
            elif type == 'addon':
                source_item = cart.cart.item_set.filter(
                    content_type=item_ct)[0]
                source_owner = source_item.product.container.owner
                dst_owner = item.list.container.owner
            else:
                source_owner = True
                dst_owner = False  # some sort of trick

            #validate source and dst owners
            if source_owner != dst_owner:
                messages.info(
                    request,
                    _("You can not order stuff with \
another services or providers")
                )
                return redirect(request.META.get('HTTP_REFERER', '/'))
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def common_owner(kw, field, allow_create=False):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            pk = kwargs[field]
            Obj = get_model(*kw['model'].lower().split('.'))
            item = get_object_or_None(Obj, pk=pk)
            if not item and allow_create:
                return func(request, *args, **kwargs)

            mapper = [item, ] + kw['check_path'].split('.')
            user = reduce(
                lambda x, y: getattr(x, y) if hasattr(x, y) else None,
                mapper
            )
            if user == request.user:
                return func(request, *args, **kwargs)
            return redirect('core:blockage')
        return wrapper
    return decorator


container_owner = partial(
    common_owner,
    kw={
        'model': 'catalog.Container',
        'check_path': 'owner'
    }
)


item_owner = partial(
    common_owner,
    kw={
        'model': 'catalog.Item',
        'check_path': 'container.owner'
    }
)

# works but very certain and uncommon way to check permission
#def item_owner(field, allow_create=False):
#    def decorator(func):
#        def wrapper(request, *args, **kwargs):
#            pk = kwargs[field]
#            item = get_object_or_None(Item, pk=pk or 0)
#            if not item and allow_create:
#                return func(request, *args, **kwargs)
#            owner = (
#               item.container.owner if hasattr(item, 'container') else None
#            )
#            if owner == request.user:
#                return func(request, *args, **kwargs)
#            return redirect('core:blockage')
#        return wrapper
#    return decorator
