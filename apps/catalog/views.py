# -*- coding: utf-8 -*-
from copy import deepcopy
from decimal import Decimal
from datetime import datetime, timedelta

from apps.geo.models import GPos
from apps.core.helpers import (
    render_to, get_model_content_type, make_http_response,
    get_object_or_None, paginate
)
from apps.catalog.helpers import is_valid
from apps.accounts.decorators import partner_required, user_fields_required
from apps.accounts.models import TimeNDay, Schedule
from apps.catalog.forms import (
    AddContainerForm, AddItemForm, OrderForm, VoteOrderForm,
    AddAddonForm, SearchPartnerOrderForm, CartItemAddForm,
    OrderUpdateForm, AddSpecialForm, AddAddonToCartForm, ImportCSVForm
)
from apps.catalog.forms import generate_vote_form
from apps.catalog.models import(
    Container, Service, Item, Order, OrderContainer,
    Vote, Addon, AddonList, Category, PaymentTransaction,
    Special, BonusTransaction,
    ORDER_STATUSES, MailCode,
)
from apps.geo.models import City
from apps.catalog.decorators import (
    not_empty_cart_required, check_provider_unique,
    item_owner, container_owner
)

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template import loader, Context
from django.http import HttpResponseRedirect, Http404
from django.db import transaction
from django.db.models import Q, F
from django.contrib import messages
from django.template.loader import render_to_string

from cart import Cart, ItemAlreadyExists, ItemDoesNotExist

from django.contrib.gis.utils import GeoIP


@render_to('index.html')
def index(request):
    return {
        'services': Service.objects.all()
    }


@render_to('catalog/service_list.html')
def service_list(request):
    return {
        'services': Service.objects.all()
    }


# helper for service_orders
def process_filter_orders(request, orders):
    # proceeding ordering
    fields = [
        'id', 'status', 'cost', 'commission', 'discount',
        'deliver_cost', 'container__owner__service_name',
        'created_on', 'offline_client__name',
        'real_commission',
    ]
    ordering = []
    for field in fields:
        porder = request.GET.get('o%s' % field)
        norder = request.GET.get('-o%s' % field)
        if porder is not None or norder is not None:
            if porder is not None:
                filter_param = field
            else:
                filter_param = '-%s' % field
            ordering.append((filter_param, porder or norder or 0))
    if ordering:
        ordering.sort()
        x = [i[0] for i in ordering]
        orders = orders.order_by(*x)  # ordering)

    return orders


# not confirmed orders
@login_required
@render_to('catalog/service_orders.html')
def service_orders_nc(request):
    dt = {}
    if not any((request.user.is_operator, request.user.is_partner)):
        raise Http404("Because I want")

    # if request.user.is_partner:
    #    return {'redirect': 'catalog:service-orders-confirmed'}

    client = request.GET.get('client', '')
    items = request.GET.get('item', '')
    min_cost = request.GET.get('min_cost', None)
    max_cost = request.GET.get('max_cost', None)
    date = request.GET.get('date', None)
    _format = request.GET.get('format', None)
    status = deepcopy(request.GET.getlist('status', []))

    statuses = ['finished', 'rejected', 'processed', 'approved']
    statuses_not_confirmed = [
        'not_confirmed',
        'checking'
    ]
    if request.user.is_partner:
        statuses.pop(statuses.index('approved'))
        statuses_not_confirmed.append('approved')
        statuses_not_confirmed.pop(statuses_not_confirmed.\
                                   index('not_confirmed'))
        statuses_not_confirmed.pop(statuses_not_confirmed.index('checking'))

    orders = Order.objects.filter(status__in=statuses_not_confirmed).\
    order_by('-id')
    offset = datetime.now() - timedelta(**settings.NOT_CONFIRMED_INTERVAL)
    orders_nc = Order.objects.filter(
        status__in=statuses_not_confirmed,
        created_on__lte=offset
    ).order_by('created_on')
    not_confirmed = orders_nc.count()

    if request.user.is_partner:
        orders = orders.exclude(status__in=['not_confirmed', 'checking'])
        not_confirmed = orders.count()
    if min_cost:
        orders = orders.filter(cost__gte=min_cost)
    if max_cost:
        orders = orders.filter(cost__lte=max_cost)
    if client:
        orders = (
            orders.filter(offline_client__name__icontains=client)
        )
    if date:
        _date = datetime.strptime(date, '%d.%m.%Y')
        _stop_date = _date + timedelta(hours=23, minutes=59, seconds=59)
        orders = orders.filter(
            created_on__gte=_date, created_on__lte=_stop_date
        )
    # filtering for partners
    if request.user.is_partner and not request.user.is_operator:
        orders = orders.filter(container__owner=request.user)
        dt.update({'_template': 'catalog/service_partner_orders.html'})

    if items:
        itemz = Item.objects.filter(title__icontains=items)
        addons = Addon.objects.filter(title__icontains=items)

        items_ct = get_model_content_type(Item)
        addon_ct = get_model_content_type(Addon)
        item_containers = OrderContainer.objects.filter(
            content_type=items_ct, object_id__in=itemz
        )
        addon_containers = OrderContainer.objects.filter(
            content_type=addon_ct, object_id__in=addons
        )

        orders = (
            orders.filter(order_container_order_set__in=item_containers) |
            orders.filter(order_container_order_set__in=addon_containers)
        ).distinct()

    if 'is_paid' in status:
        orders = orders.filter(is_paid=True)
        status.pop(status.index('is_paid'))

    if status:
        orders = orders.filter(
            Q(status__in=status)  # | Q(is_paid=is_paid)
        )
    total_price = sum([i['cost'] - i.get('discount', 0) for i in
                       orders.values('cost', 'discount')])

    orders = process_filter_orders(request, orders)
    if _format == 'csv':
        return {
            '_template': 'catalog/service_orders.csv',
            '_content_type': 'text/csv',
            'orders': orders
        }
    dt.update({
        'orders': orders,
        'orders_nc': orders_nc,
        'total_price': total_price,
        'not_confirmed': not_confirmed,
        'ORDERS': ORDER_STATUSES,
        'G': request.GET,
        'status': request.GET.getlist('status', []),
    })
    return dt


@login_required
@render_to('catalog/service_orders.html')
def service_orders(request):
    dt = {}
    if not any((request.user.is_operator, request.user.is_partner)):
        raise Http404("Because I want")
    status = deepcopy(request.GET.getlist('status', ''))
    client = request.GET.get('client', '')
    items = request.GET.get('item', '')
    min_cost = request.GET.get('min_cost', None)
    max_cost = request.GET.get('max_cost', None)
    date = request.GET.get('date', None)
    _format = request.GET.get('format', None)

    excludes = ['not_confirmed',
        'approved',
        'checking'
    ]
    statuses = [
        'approved',
        'finished',
        'rejected',
        'processed',
    ]

    if request.user.is_partner:
        # excludes.pop(excludes.index('approved'))
        statuses.pop(statuses.index('approved'))
        if settings.HIDE_REJECTED_FROM_PARTNER:
            excludes.append('rejected')
    if request.user.is_operator:
        excludes.pop(excludes.index('approved'))

    is_paid = ('is_paid' in status)
    if is_paid:
        status.pop(status.index('is_paid'))

    orders = Order.objects.order_by('-id')

    orders = orders.filter(status__in=statuses)
    if is_paid:
        orders = orders.filter(is_paid=is_paid)

    # if request.user.is_partner:
    #    orders = orders.exclude(status='rejected')
    not_confirmed = orders.filter(status='not_confirmed').count()
    if min_cost:
        orders = orders.filter(cost__gte=min_cost)
    if max_cost:
        orders = orders.filter(cost__lte=max_cost)
    if status:
        orders = orders.filter(status__in=status)
    if client:
        orders = (
            orders.filter(offline_client__name__icontains=client)
        )
    if date:
        _date = datetime.strptime(date, '%d.%m.%Y')
        _stop_date = _date + timedelta(hours=23, minutes=59, seconds=59)
        orders = orders.filter(
            created_on__gte=_date, created_on__lte=_stop_date
        )

    # filtering for partners
    if request.user.is_partner and not request.user.is_operator:
        orders = orders.filter(container__owner=request.user)
        dt.update({'_template': 'catalog/service_partner_orders.html'})

    if items:
        itemz = Item.objects.filter(title__icontains=items)
        addons = Addon.objects.filter(title__icontains=items)

        items_ct = get_model_content_type(Item)
        addon_ct = get_model_content_type(Addon)
        item_containers = OrderContainer.objects.filter(
            content_type=items_ct, object_id__in=itemz
        )
        addon_containers = OrderContainer.objects.filter(
            content_type=addon_ct, object_id__in=addons
        )

        orders = (
            orders.filter(order_container_order_set__in=item_containers) |
            orders.filter(order_container_order_set__in=addon_containers)
        ).distinct()

    total_price = sum([i['cost'] - i.get('discount', 0) for i in
                       orders.values('cost', 'discount')])
    orders = process_filter_orders(request, orders)

    if _format == 'csv':
        return {
            '_template': 'catalog/service_orders.csv',
            '_content_type': 'text/csv',
            'orders': orders
        }

    dt.update({
        'orders': orders,
        'total_price': total_price,
        'not_confirmed': not_confirmed,
        'ORDERS': ORDER_STATUSES,
        'G': request.GET,
        'status': request.GET.getlist('status', []),
        'has_status': True
    })
    return dt


@login_required
@render_to('catalog/order_info.html')
def service_order_info(request, pk):
    if not any((request.user.is_operator, request.user.is_partner)):
        raise Http404("Because you don't")
    order = get_object_or_404(Order, pk=pk)
    order_statuses = []
    for (code, description) in ORDER_STATUSES:
        order_statuses.append(dict(code=description))
    return {
        'order': order,
        'order_statuses': ORDER_STATUSES
    }


@login_required
@render_to('catalog/order_info.html', allow_xhr=True)
def service_order_update(request, pk):
    if not any((request.user.is_operator, request.user.is_partner)):
        raise Http404("MUHAHAHA")
    order = get_object_or_404(Order, pk=pk)
    if (order.container.owner != request.user) and not request.user.is_operator:
        raise Http404("not allowed")
    form = OrderUpdateForm(request.POST or None, instance=order)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            # return {'form': form}
    return {
        'order': order, 'form': form,
        'order_statuses': ORDER_STATUSES
    }


def get_service_data(request, pk, title='', category_pk=None):
    service = get_object_or_404(User, pk=pk, is_partner=True)
    votes = Vote.objects.filter(
        order__container__in=service.containers.all(),
        is_approved=True
    )
    containers = Container.objects.filter(
    #    container=None,
        owner=service,
        service=service.service).order_by('title').distinct('title')
    if title:
        containers = containers.filter(title__iexact=title)
        containers = (
            Container.objects.filter(pk__in=containers) |
            Container.objects.filter(container__in=containers)
        )
    if category_pk:
        containers = containers.filter(pk=category_pk)
        containers = (
            Container.objects.filter(pk__in=containers) |
            Container.objects.filter(container__in=containers)
        )
    items = Item.objects.filter(container__in=containers)
    addon_lists = AddonList.objects.filter(container__in=containers)
    addons = Addon.objects.filter(list__in=addon_lists)

    return {
        'service': service,
        'votes': votes,
        'containers': containers,
        'items': items,
        'addons': addons,
    }


@render_to('catalog/all_specials.html')
def all_specials(request, service_name):
    if not service_name:
        return dict(redirect=reverse('catalog:all-specials',
                 kwargs=dict(service_name=Service.objects.all()[0].codename)))
    try:
        service = Service.objects.get(codename=service_name)
    except Service.DoesNotExist:
        service = None
    city_id = request.session.get('city', None)
    if not city_id:
        try:
            city_id = request.user.city.id
        except AttributeError:
            return dict(redirect=reverse('index'))
    specials = Special.objects.filter(is_active=True, owner__city__id=city_id)
    if service:
        specials = specials.filter(owner__service=service)
    page = request.GET.get('page', '1')
    page = int(page) if page.isdigit() else 1

    specials = paginate(specials, page,
                        pages=settings.SPECIALS_OBJECTS_ON_PAGE)
    dt = {'specials': specials, 'services': Service.objects.all(),
          'service_name': service_name}
    if settings.SAUSAGE_SCROLL_ENABLE and int(page) != 1:
        dt.update({'_template': 'catalog/include/specials.html'})
    return dt


@login_required
@partner_required
@render_to('catalog/service_partner_specials.html')
def service_partner_specials(request, pk):
    dt = get_service_data(request, pk)
    items = dt['items']
    items = items.filter(is_special_active=True)
    page = request.GET.get('page', 1)
    items = paginate(items, page, pages=settings.ITEMS_ON_PAGE)
    dt['items'] = items
    return dt


@login_required
@partner_required
@render_to('catalog/special_add.html')
def special_add(request, pk=None):
    instance = get_object_or_None(Special, pk=pk)
    if instance and instance.owner != request.user:
        raise Http404("not allowed")
    form = AddSpecialForm(
        request.POST or None, request.FILES or None,
        instance=instance
    )
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.save()
            return {
                'redirect': 'catalog:service-partner-specials',
                'redirect-args': (request.user.pk,)
            }
    return {'form': form}


@login_required
@partner_required
@render_to('catalog/special_add.html')
def special_del(request, pk):
    special = get_object_or_404(Special, pk=pk)
    if request.user != special.owner:
        raise Http404("Nonono")
    pk = special.owner.pk
    special.delete()
    return {
        'redirect': 'catalog:service-partner-specials',
        'redirect-args': (pk,)
    }


@render_to('catalog/service_page.html')
def service_page(request, pk, title='', category_pk=None):
    dt = get_service_data(
        request, pk=pk, title=title, category_pk=category_pk
    )
    items = dt['items']
    items = items.order_by('container__weight', 'weight', '-id')
    page = request.GET.get('page', 1)
    items = paginate(items, page, pages=settings.ITEMS_ON_PAGE)
    dt['items'] = items
    if settings.SAUSAGE_SCROLL_ENABLE and int(page) != 1:
        dt.update({'_template': 'catalog/include/service_page_items.html'})
    return dt


@render_to('catalog/service_rating.html')
def service_rating(request, pk):
    """ shows Owner-service rating, not whole Service instance ratings """
    # service = get_object_or_404(User, pk=pk, is_partner=True)
    # votes = Vote.objects.filter(
    #    order__container__in=service.containers.all(),
    #    is_approved=True
    # )
    # codename = service.service.codename or service.service.pk
    # containers = Container.objects.filter(
    #    container=None,
    #    service=service.service).order_by('title').distinct('title')
    return get_service_data(request, pk)  # {
    #    'service': service,
    #    'votes': votes,
    #    'containers': containers,
    #    'border_inc': 'catalog/flags/%s_list.html' % codename
    # }


@render_to('catalog/service_about.html')
def service_about(request, pk):
    return get_service_data(request, pk)


@render_to('catalog/service_specials.html')
def service_specials(request, pk):
    return get_service_data(request, pk)


@render_to('catalog/catalog_list.html')
def catalog_list(request, service_pk=0, codename='', is_special=False):
    service = (
        get_object_or_None(Service, pk=service_pk)
        or get_object_or_None(Service, codename=codename)
    )
    search_type = request.GET.get('search-type', 0)
    is_special = request.GET.get('is_special', is_special)
    cardpay = request.GET.get('cardpay', False)

    # container_list = request.GET.getlist('type') or None
    categories_list = request.GET.getlist('type', [])
    categories_list = categories_list if all(categories_list) else []

    minimal_cost = request.GET.get('minimal_cost', 0)
    title = request.GET.get('title', '')
    by_rating = request.GET.get('by_rating', False)
    nlat, mlat, nlng, mlng = map(request.GET.get, ['nlat', 'mlat', 'nlng',
                                                   'mlng'])

    free_deliver = request.GET.get('free_deliver', False)
    state = request.GET.get('state', 1)

    if not service:
        raise Http404("No such service found")

    # select only that cities where user is bind to
    geoip = GeoIP()
    ip = request.GET.get('REMOTE_ADDR', '127.0.0.1')
    city = request.session.get(
        'city',
        request.user.city
        if request.user.is_authenticated() else \
        (geoip.city(ip) or {}).get('city', None)
    )

    containers = Container.objects.filter(
        service=service, owner__is_published=True).order_by('owner') #@TODO: select_related

    state = int(state) if isinstance(state, basestring) else 1
    if state:
        now = datetime.now().replace(second=0, microsecond=0)
        week_day = now.isoweekday()
        prev_week_day = week_day - 1 if week_day > 1 else 7
        qset = (
            # since < until
            Q(until__gte=now, since__lte=now, weekday=week_day) |
            # since > until
            (Q(until__lt=F('since')) &
             Q(since__lte=now, weekday=week_day)) |
            # next day jump
            (Q(until__lt=F('since')) &
             Q(until__gte=now, weekday=prev_week_day))

        )
        td = TimeNDay.objects.filter(
            Q(is_active=True) & qset
        )
        schedules = Schedule.objects.filter(timenday_schedule_set__in=td)
        containers = containers.filter(owner__schedule_user_set__in=schedules)

    if by_rating:
        containers = containers.order_by('-mean_rating')

    if city:
        containers = containers.filter(owner__city=city)
    else:
        top_city = City.objects.all()[0]
        containers = containers.filter(owner__city=top_city)

    if free_deliver:
        containers = containers.exclude(owner__avarage_cost=None)
        # containers = containers.filter(owner__avarage_deliver_cost=0)

    unique_containers = containers.filter(
        container=None).order_by('title').distinct('title')

    if categories_list:
        categories = Category.objects.filter(pk__in=categories_list)
        categories = categories | \
            Category.objects.filter(parent__in=categories)  # 2 lvl
        categories = categories | \
            Category.objects.filter(parent__in=categories)  # 3 lvl
        containers = containers.\
            filter(category__in=categories)  # categories_list)
        # containers = (
        #    containers.filter(container__title__in=container_list) |
        #    containers.filter(title__in=container_list)
        # )

    if isinstance(minimal_cost, basestring):
        minimal_cost = int(minimal_cost) if minimal_cost.isdigit() else 0
    if minimal_cost:
        # owner__avarage_cost__lte=minimal_cost)
        containers = containers.filter(owner__minimal_cost__lte=minimal_cost)
    if cardpay:
        containers = containers.exclude(owner__has_online_payment=False)
    if all((nlat, mlat, nlng, mlng)):
        positions = GPos.objects.filter(
            lat__gte=nlat, lat__lte=mlat,
            lng__gte=nlng, lng__lte=mlng
        )
        containers = containers.filter(owner__gpos_user_set__in=positions)
        # containers = (
        #    containers.filter(
        #        owner__glat__gte=nlat, owner__glat__lte=mlat,
        #        owner__glng__gte=nlng, owner__glng__lte=mlng
        #    )
        # )
    has_coords = 'nlat' in request.GET
    has_coords = has_coords and 'mlat' in request.GET
    has_coords = has_coords and 'nlng' in request.GET
    has_coords = has_coords and 'mlng' in request.GET
    if has_coords and not all((nlat, mlat, nlng, mlng)):
        containers = Container.objects.filter(id= -1)
    items = Item.objects.filter(container__in=containers)

    new_ones = request.GET.get('new_ones', False)
    one_week = datetime.now() - timedelta(weeks=1)

    if search_type == '1':  # by items
        items = items.filter(
            title__icontains=title
        )
        if new_ones:
            items = items.filter(container__owner__publish_date__gte=one_week)
        if is_special:
            items = items.filter(is_special_active=True)  
    else:  # by containers
        containers = containers.filter(
            owner__service_name__icontains=title).order_by(
            'owner').distinct('owner')

        if new_ones:
            containers = containers.filter(owner__publish_date__gte=one_week)

        if is_special:
            items = Item.objects.filter(is_special_active=True,
                                        container__service=service)
            pks = containers.exclude(owner__special_owner_set=None)
            containers = (
                Container.objects.filter(item_container_set__in=items) |
                Container.objects.filter(pk__in=pks)
            )
        if by_rating:
            containers = containers.order_by('-mean_rating')
        # containers = containers.filter(item_container_set__in=items)

    page = request.GET.get('page', 1)
    containers = Container.objects.filter(
        pk__in=containers).distinct().order_by('-mean_rating').distinct()

    categories = Category.objects.filter(service=service)

    # ordering
    items = Item.objects.filter(
        pk__in=items.order_by('-cost').values('pk')
        ).distinct().order_by('-cost')
    order_by = request.GET.get('order_by', '-cost')
    order_by_asc = not order_by.startswith('-')
    if not order_by_asc:
        order_by = order_by[1:]
        order_by_prefix = '-'
        order_by_prefix_future = ''
    else:
        order_by_prefix = ''
        order_by_prefix_future = '-'
    if order_by in settings.CATALOG_ORDER_BY:
        items = items.order_by(order_by_prefix + order_by)
    if by_rating:
        items = items.order_by('-container__mean_rating')             
    # paging
    containers = paginate(containers, page, pages=settings.DEFAULT_PAGES_COUNT)
    items = paginate(items, page, pages=settings.DEFAULT_PAGES_COUNT)
    dt = {
        'service': service,
        'categories': categories,
        'containers': containers,
        'items': items,
        'unique_containers': unique_containers,
        'search_type': search_type,
        'types': [int(i if i.isdigit() else 0) for i in
                  request.GET.getlist('type')],
        'G': request.GET,
        'request': request,
        'order_by': order_by,
        'order_by_prefix': order_by_prefix,
        'order_by_prefix_future': order_by_prefix_future,
    }
    if settings.SAUSAGE_SCROLL_ENABLE:
        if int(search_type) == 1 and int(page) != 1:
            dt.update({'_template': 'catalog/include/items.html'})
        elif int(page) != 1:
            dt.update({"_template": "catalog/include/partners.html"})
    return dt


@login_required
@user_fields_required(['service', ])
@partner_required
@render_to('catalog/partner_categories.html')  # container_list.html')
def container_list(request):
    containers = Container.objects.filter(
        owner=request.user, container=None
    )
    categories = Category.objects.filter(
        service=request.user.service
    )
    return {
        'containers': containers,
        'categories': categories
    }


@login_required
@user_fields_required(['service', ])
@partner_required
@render_to('catalog/container.html')
def container(request, pk):
    container = get_object_or_404(Container, pk=pk)
    containers = Container.objects.filter(
        owner=request.user, container=None
    )
    categories = Category.objects.filter(service=request.user.service)

    return {
        'container': container,
        'containers_list': containers,
        'categories': categories
    }


@render_to('catalog/addon_list.html')
@login_required
def addon_list(request, pk):
    container = get_object_or_404(Container, pk=pk)
    item_pk = request.GET.get('item', None)
    item = get_object_or_404(Item, pk=item_pk) if item_pk else None

    form = AddAddonForm(
        request.POST or None, request=request, initial={
            'container': container
        }
    )
    return {
        'addons': Addon.objects.filter(
            list__container=container
        ),
        'container': container,
        'item': item,
        'form': form
    }


@login_required
@container_owner(field='pk')
@user_fields_required(['service', ])
@partner_required
@render_to('catalog/container_add.html', allow_xhr=True)
def container_edit(request, pk):
    container = get_object_or_404(Container, pk=pk)
    if container.owner != request.user:
        raise Http404("not allowed")
    form = AddContainerForm(
        request.POST or None, instance=container,
        request=request)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            redirect = form.cleaned_data.get('next', None)
            if redirect:
                return {'redirect': redirect}
            return {'redirect': 'catalog:container-list'}
    return {'form': form}


@login_required
@container_owner(field='pk')
@user_fields_required(['service', ])
@partner_required
@render_to('index.html')
def container_delete(request, pk):
    container = get_object_or_404(Container, pk=pk)
    container.delete()
    return {'redirect': 'catalog:container-list'}


@login_required
@user_fields_required(['service', ])
@partner_required
@render_to('catalog/container_add.html', allow_xhr=True)
def container_add(request, pk=None):
    container = get_object_or_404(Container, pk=pk) if pk else None
    if container:
        if container.owner != request.user:
            raise Http404("not allowed")
    form = AddContainerForm(request.POST or None, initial={
        'container': container
    }, request=request)
    if request.method == 'POST':
        if form.is_valid():
            container = form.save(commit=False)
            container.owner = request.user
            container.service = request.user.service
            container.save()
            redirect = form.cleaned_data.get('next', None)
            if redirect:
                return {'redirect': redirect}
            return {'redirect': 'catalog:container-list'}
    return {
        'form': form
    }


@partner_required
@render_to('catalog/service_specials.html')
@login_required
@item_owner(field='pk')
def item_special_off(request, pk):
    item = get_object_or_404(Item, pk=pk)
    item.is_special_active = False
    item.save()
    redr = reverse('catalog:service-specials', args=(request.user.pk,))
    return {'redirect': redr}


@login_required
@user_fields_required(['service', ])
@partner_required
@render_to('catalog/item_add.html')
def item_add(request, pk=None):
    container = get_object_or_404(Container, pk=pk) if pk else None
    if container:
        if container.owner != request.user:
            raise Http404("not allowed")
    form = AddItemForm(request.POST or None, request.FILES or None, initial={
        'container': container or None
    })

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return {
                'redirect': 'catalog:container',
                'redirect-args': (form.instance.container.pk,)
            }
    return {'form': form}


@item_owner(field='pk')
@partner_required
@render_to('index.html')
@login_required
def item_delete(request, pk=None):
    item = get_object_or_404(Item, pk=pk)
    url = reverse('catalog:container', args=(item.container.pk,))
    item.is_deleted = True  # delete()
    item.save()
    return {'redirect': url}


@render_to('catalog/item_description_popup.html')
def item_description_popup(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return {'item': item}


@login_required
@item_owner(field='pk')
@user_fields_required(['service', ])
@partner_required
@render_to('catalog/item_add.html')
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.container.owner != request.user:
        raise Http404("not allowed")
    form = AddItemForm(
        request.POST or None, request.FILES or None, instance=item
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
        return {
            'redirect': 'catalog:container',
            'redirect-args': (form.instance.container.pk,)
        }
    return {'form': form}


@partner_required
@login_required
@render_to('catalog/addon_add.html')
def addon_add(request, pk=None):
    container = get_object_or_None(Container, pk=pk)
    if container.owner != request.user:
        raise Http404("not allowed")
    form = AddAddonForm(
        request.POST or None, request=request, initial={
            'container': container
        }
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return {
                'redirect': 'catalog:addon-list',
                'redirect-args': (form.cleaned_data['container'].pk,)
            }

    return {'form': form}


@login_required
@partner_required
@render_to('catalog/addon_add.html')
def addon_edit(request, pk):
    instance = get_object_or_404(Addon, pk=pk)
    if instance.category.container.owner != request.user:
        raise Http404("not allowed")
    form = AddAddonForm(
        request.POST or None, instance=instance, request=request,
        initial={
            'container': instance.list.container.pk
        }
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return {
                'redirect': 'catalog:addon-list',
                'redirect-args': (form.cleaned_data['container'].pk,)
            }
    return {'form': form}


@login_required
@partner_required
@render_to('catalog/addon_list.html')
def addon_delete(request, pk=None):
    addon = get_object_or_404(Addon, pk=pk)
    if addon.list.container.owner != request.user:
        raise Http404("Nonono")

    container_pk = addon.list.container.pk
    addon.is_deleted = True
    addon.save()
    return {
        'redirect': 'catalog:addon-list',
        'redirect-args': (container_pk,)
    }


@render_to('index.html', allow_xhr=True)
def cart_item_add(request):
    form = CartItemAddForm(request.POST or None, request=request)
    if request.method == "POST":
        print request.META.get('HTTP_REFERER', '/')
        if form.is_valid():
            add_item_to_cart(
                request,
                item_pk=form.cleaned_data['item'],
                quantity=form.cleaned_data['quantity']
            )
        else:
            return {'form': form}
    return {'redirect': request.META.get('HTTP_REFERER', '/')}


def cart_cleanse(request):
    cart = Cart(request)
    cart.cart.item_set.all().delete()
    return redirect(request.META.get("HTTP_REFERER", '/'))


@check_provider_unique(field='item_pk')
@render_to('catalog/cart.html', allow_xhr=True)
def add_item_to_cart(request, item_pk, quantity=1, checkout=False):
    cart = Cart(request)
    item = get_object_or_404(Item, pk=item_pk)
    # checking input data, validate it and raise error if something
    # goes unusual, without any data post for time measure resons
    threshold = item.category.threshold
    try:
        quantity = int(quantity)
    except TypeError:
        raise Http404("Go fsck yourself")
    if int(quantity) < threshold:
        msg = _("You can not order less of item quantity then "
        "given threshold"
        )
        return {'success': False, 'errors': unicode(msg)}
    if int(quantity) % threshold != 0:
        msg = _(
            "Quantity should be proportional to its item category threshold, "
            "you can not add items without it"
        )
        return {'success': False, 'errors': unicode(msg)}
    ct = ContentType.objects.get(
        app_label=Item._meta.app_label,
        model=Item._meta.module_name)
    try:
        cart.add(item, item.get_cost(), quantity)
    except ItemAlreadyExists:
        cart_item = cart.cart.item_set.get(object_id=item_pk, content_type=ct)
        if checkout:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        cart_item.save()
        return {'redirect': 'catalog:cart'}
    return {'redirect': request.META.get('HTTP_REFERER', '/')}


@check_provider_unique(field='addon_pk', type='addon')
def add_addon_to_cart(request, addon_pk, quantity=1, checkout=False):
    cart = Cart(request)
    addon = get_object_or_404(Addon, pk=addon_pk)
    # item = get_object_or_404(Item, pk=item_pk)
    addon_ct = get_model_content_type(Addon)
    # item_ct = get_model_content_type(Item)
    try:
        # cart.add(addon, addon.cost, quantity, item_ct, item.pk)
        cart.add(addon, addon.get_cost(), quantity)
    except ItemAlreadyExists:
        cart_item = cart.cart.item_set.get(
            object_id=addon_pk, content_type=addon_ct
        )
        if checkout:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        cart_item.save()
        return redirect('catalog:cart')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@csrf_exempt
@render_to('index.html', allow_xhr=True)
def add_addons_to_cart(request):
    form = AddAddonToCartForm(request.POST or None, request=request)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return {'success': True}
    return {
        'form': form
    }


def remove_item_from_cart(request, item_pk):
    cart = Cart(request)
    item = get_object_or_404(Item, pk=item_pk)
    item_ct = get_model_content_type(Item)
    addon_ct = get_model_content_type(Addon)
    try:
        cart.remove(item)
        items = cart.cart.item_set.filter(content_type=item_ct).count()
        if items == 0:
            # remove all addons if items drops to zero
            cart.cart.item_set.filter(content_type=addon_ct).delete()
    except ItemDoesNotExist:
        return redirect('catalog:cart')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def remove_addon_from_cart(request, addon_pk):
    cart = Cart(request)
    item = get_object_or_404(Addon, pk=addon_pk)
    try:
        cart.remove(item)
    except ItemDoesNotExist:
        return redirect('catalog:cart')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


# @render_to('catalog/cart.html')
@render_to('catalog/service_page.html')
def cart(request):
    _cart = Cart(request)
    item_ct = get_model_content_type(Item)

    products = _cart.cart.item_set.filter(content_type=item_ct)
    context = {
        'cart': _cart, 'total_price': _cart.get_total_price(),
        'products': products,
    }
    if products:
        service = products.all()[0].product.container.owner
        return {
            'redirect': 'catalog:service-page',
            'redirect-args': (service.pk,)
        }
    else:
        context.update({
            '_template': 'catalog/cart.html'
        })
    return context


@transaction.commit_on_success
# @not_empty_cart_required
# @login_required
@render_to('catalog/order_popup.html')
def order_popup(request):
    return {}


#
@transaction.commit_on_success
@not_empty_cart_required
# @login_required
@render_to('catalog/order.html', allow_xhr=True)
def order(request):
    form = OrderForm(request.POST or None, request=request)
    if request.method == 'POST':
        if form.is_valid():
            order = form.save(commit=False)
            cart = Cart(request)
            item_ct = get_model_content_type(Item)
            addon_ct = get_model_content_type(Addon)

            for item in cart.cart.item_set.filter(content_type=item_ct):
                container = item.product.container
                service = container.service
                break
            order.service = service
            order.container = container
            order.offline_client = form.save_offline_client()
            order.commission = container.owner.commission
            order.save()
            # generating discount
            discount = form.cleaned_data['discount'] or 0
            if discount:
                discount_transaction = BonusTransaction.objects.create(
                    client=request.user,
                    order=order,
                    amount=str(discount * -1),
                    is_processed=False,
                    is_discount=True,
                    description='discount'
                )
                if order.client:
                    order.client.reload_bonus_score(rebuild=True)
            order.generate_vote_instance()

            # saving items and addons as order relations
            # savin items
            # for item in cart.cart.item_set.filter(content_type=item_ct):
            #    order_container = OrderContainer.objects.create(
            #        content_type=item_ct, object_id=item.product.pk,
            #        quantity=item.quantity,
            #        total_price=item.total_price,
            #        order=order)
            #
            # savin addons separate inside of items
            # for addon in cart.cart.item_set.filter(content_type=addon_ct):
            #    order_container_item = OrderContainer.objects.get(
            #        content_type=item_ct,
            #        object_id=addon.link.pk, order=order)
            #    order_container = OrderContainer.objects.create(
            #        parent=order_container_item,
            #        content_type=addon_ct,
            #        object_id=addon.product.pk,
            #        total_price=addon.total_price,
            #        order=order)
            for item in cart:
                if isinstance(item.product, Item):
                    order_container = OrderContainer.objects.create(
                        content_type=item_ct, object_id=item.product.pk,
                        quantity=item.quantity,
                        total_price=item.total_price,
                        order=order)
                    # for x in range(item.quantity):
                    #    order.items.add(item.product)
                elif isinstance(item.product, Addon):
                    order_container = OrderContainer.objects.create(
                        content_type=addon_ct, object_id=item.product.pk,
                        quantity=item.quantity,
                        total_price=item.total_price,
                        order=order)
                    # for x in range(item.quantity):
                    #    order.addons.add(item.product)
                else:
                    pass

            cart.delete_items()
            if order.status == 'not_confirmed':
                for i in User.objects.filter(is_operator=True):    
                    emails = i.get_emails()
                    phone = order.container.owner.phone
                    link = reverse('catalog:service-orders')
                    message = EmailMultiAlternatives(
                        unicode(_(u"Поступил новый заказ")),
                        render_to_string(settings.NEW_ORDER_MESSAGE_TEMPLATE_NAME,
                {'link': link, 'object': order, 'order_statuses': ORDER_STATUSES,
                'site_url': settings. SITE_URL,
                 }),
                        settings.EMAIL_FROM,
                        emails,
                    )
                    message.content_subtype = 'html'
                    message.send(fail_silently=True)                      
            if form.cleaned_data['payment_redirect'] == 'online':
                order = form.instance
                url = order.get_online_payment_url()
                return {
                    'payment_redirect': url,
                    'order_id': form.instance.pk,
                    'order_amount': order.cost
                }
            return {
                # 'redirect': 'catalog:order-success',
                'order_id': form.instance.pk,
                'order_amount': order.cost
            }
    addon_ct = get_model_content_type(Addon)
    item_ct = get_model_content_type(Item)
    cart = Cart(request)
    products = cart.cart.item_set.filter(content_type=item_ct)
    addons = cart.cart.item_set.filter(content_type=addon_ct)

    return {
        'form': form,
        'products': products,
        'addons': addons
    }


@transaction.commit_on_success
@login_required
def order_repeat(request, pk):
    order = get_object_or_404(Order, pk=pk)
    containers = order.order_container_order_set.all()
    cart = Cart(request)
    if cart.cart.item_set.count() != 0:
        messages.error(
            request, _("You can not repeat order if there's something "
            "in the cart, please cleanse it")
        )
        # return redirect(request.META.get('HTTP_REFERER', '/'))
        return redirect(reverse('catalog:service-page',
                                args=(order.container.owner.pk,)))
    for container in containers:
        model_class = container.content_type.model_class()
        item = get_object_or_None(
            model_class.whole_objects, pk=container.object_id
        )
        if item.is_deleted:
            messages.warning(
                request, _("Item '%s' does not exist anymore, sorry") % \
                    item.title
            )
        else:
            cart.add(item, item.get_cost(), container.quantity)
    # return redirect(request.META.get('HTTP_REFERER', '/'))
    return redirect(reverse('catalog:service-page',
                            args=(order.container.owner.pk,)))


@login_required
@partner_required
@csrf_exempt
@render_to('catalog/orders_partner.html')
def orders_partner(request):
    form = SearchPartnerOrderForm(request.GET or None)
    orders = Order.objects.filter(container__owner=request.user)
    if request.method == 'GET':
        data = request.GET
        # fast and beauty way to get non-null data values in keys
        # if (sys.version_info.major, sys.version_info.minor) >= (2, 7):
        #    search_data = {
        #        key: value for key, value
        #        in data.items() if value
        #    }
        search_data = {}
        for key, value in data.items():
            if value:
                search_data.update({key: value})
        orders = orders.filter(Q(**search_data))
    return {
        'orders': orders,
        'form': form,
        'GET': "&".join(
            [
                "%s=%s" % (k, request.GET[k]) for k in request.GET.keys()
            ]
        )
        # Order.objects.filter(container__owner=request.user)
    }


@login_required
@partner_required
def orders_partner_csv(request):
    response = make_http_response(content_type='text/html')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'

    orders = Order.objects.filter(container__owner=request.user)
    if request.method == 'GET':
        data = request.GET
        # if (sys.version_info.major, sys.version_info.minor) >= (2, 7):
        #    search_data = {
        #        key: value for key, value
        #        in data.items() if value
        #    }
        # else:  # python 2.6 sucks
        search_data = {}
        for key, value in data.items():
            if value:
                search_data.update({key: value})

        orders = orders.filter(Q(**search_data))

    t = loader.get_template('csv/orders_partner.csv')
    c = Context({
        'orders': orders
    })
    response.write(t.render(c))
    return response


@login_required
@render_to('catalog/orders.html')
def orders(request):
    """ user order list """
    orders = Order.objects.filter(
        client=request.user).order_by('-created_on', 'status'
    )
    orders = process_filter_orders(request, orders)
    return {
        'orders': orders,
        'ORDERS': ORDER_STATUSES
    }


@login_required
@render_to('catalog/order_vote.html')
def order_vote(request, sid):
    """ vote for order """
    vote = get_object_or_404(Vote, sid=sid, is_proceeded=False)
    if settings.ALLOW_SUPERUSER_VOTE:
        if vote.client != request.user and not request.user.is_superuser:
            raise Http404("Not allowed")
    else:
        if vote.client != request.user:
            raise Http404("Not allowed")

    dt = get_service_data(request, pk=vote.order.container.owner.pk)
    dt.update({'_template': 'catalog/service_rating.html'})
    form_class = generate_vote_form(vote, VoteOrderForm)
    form = form_class(request.POST or None, instance=vote)
    # VoteOrderForm(request.POST or None, instance=vote)
    if request.method == 'POST':
        if form.is_valid():
            form.save(commit=False)
            instance = form.instance
            instance.is_proceeded = True
            instance.save()
            # making message
            messages.info(
                request, _("Thank you, your vote proceeded")
            )
            return dt  # {'redirect': 'catalog:order-vote-success'}

    dt.update({
        'vote_form': form,
    })
    return dt


@transaction.commit_on_success
@csrf_exempt
def order_payment_notification(request):
    success = ('<?xml version="1.0" encoding="UTF-8"?>'
        "<result>"
        "<code>{code}</code>"
        "</result>"
    )
    error = ('<?xml version="1.0" encoding="UTF-8"?>'
        "<result>"
        "<code>{code}</code>"
        "<comment>{comment}</comment>"
        "</result>"
    )
    # # verbose version:
    # response = '''
    # <?xml version="1.0" encoding="UTF-8"?>
    # <result>
    # <id>{id}</id>
    # <code>{code}</code>
    # <comment>{comment}</comment>
    # <course>{course}</course>
    # </result>
    # '''
    response = make_http_response(content_type='text/xml')
    if request.method != 'POST':
        response.write(
            error.format(
                code= -1,
                comment='no allowed method %s' % request.method
            )
        )
        return response
    data = request.POST
    # IMPORTANT: ensure 'code' calculation algorithm below remains idempotent
    valid = is_valid(data)
    code = valid and 'YES' or 'NO'
    order_id = data.get('orderid')  # internal order id, string (64)
    payment_id = data.get('paymentid')  # external order id, int (30)
    amount = data.get('amount', '0')
    comment_error = ''
    if not valid:
        comment_error = "key sum is invalid"

    # payment processing logic here, whatever you need
    out = success.format(
        # id='',  # internal payment id - optional, string (64)
        code=code,
        # comment='',  #  optional, string (400)
        # course='',  #  optional, float (10.2)
    ) if valid else error.format(
        code=code,
        comment=comment_error
    )
    response.write(out)

    # proceeding payment
    if valid:
        order = get_object_or_None(Order, pk=order_id)
        amount = Decimal(str(amount))
        if order:
            order.is_paid = True
            order.save()
            kw = dict(
                amount=amount, client=order.client,
                partner=order.container.owner,
                order=order,
                payment_id=payment_id

            )
            payment = PaymentTransaction.objects.filter(**kw)
            if not payment:
                PaymentTransaction.objects.create(**kw)
    return response


@transaction.commit_on_success
@login_required
@partner_required
@render_to('catalog/csv_import.html')
def csv_import(request):
    form = ImportCSVForm(request.POST or None, request.FILES or None,
                         request=request)
    dt = {'form': form}
    if form.is_valid():
        # proceed form
        form.save()
        dt.update({'success': True, 'stats': form.stats})
    return dt


@render_to('catalog/include/addons.html')
def get_addons(request, pk):
    container = get_object_or_None(Container, pk=pk)
    addon_list = AddonList.objects.filter(container=container)
    addons = Addon.objects.filter(list__in=addon_list)
    return {
        'addons': addons
    }


@transaction.commit_on_success
@render_to('catalog/update_order_status.html')
def update_order_status(request, pk, status):
    mail_code = request.GET.get('mail_code', None)
    mail_code_obj = get_object_or_404(MailCode, uuid=mail_code)
    order = get_object_or_404(Order, pk=pk)

    if status in [i for i, j in ORDER_STATUSES]:
        order.status = status
        order.save()
        mail_code_obj.delete()
    return dict(order=order)
