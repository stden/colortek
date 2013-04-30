from datetime import datetime, timedelta
from apps.core.helpers import (
    render_to, make_http_response, model_json_encoder,
    render_to_json, get_object_or_None
)
from apps.catalog.helpers import copy_fields
from apps.catalog.models import Container, Item, Order
from apps.catalog.forms import CoordinatesForm
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.models import User
from django.conf import settings


@render_to_json(content_type='application/json')
def container(request, pk):
    container = get_object_or_None(Container, pk=pk)
    options = Container.objects.filter(
        owner=container.owner, container=None).values('pk', 'title')
    options = [{'value': i['pk'], 'title': i['title']} for i in options]
    fields = [
        'id', 'title', 'description', 'service_id', 'pk',
        'owner_id', 'mean_rating', 'category_id', 'weight',
    ]
    container = copy_fields(container, fields)

    return {
        'container': container,
        'options': options
    }


@render_to_json(content_type='application/json')
def item(request, pk):
    item = get_object_or_None(Item, pk=pk)
    if item:
        item.__dict__.update({'service_name': item.container.owner.service.codename})
    return item

@csrf_exempt
@render_to_json(content_type='application/json')
def order_price(request, pk):
    user = get_object_or_None(User, pk=pk)
    if not user:
        return {'status': 'failed', 'success': False}
    form = CoordinatesForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            lat = form.cleaned_data['lat']
            lng = form.cleaned_data['lng']
            data = user.get_deliver_price(lat, lng)
            return data
    return {'form': form, 'success': not bool(form.errors)}

@render_to_json(content_type='application/json')
def orders_not_confirmed(request):
    offset = datetime.now() - timedelta(**settings.NOT_CONFIRMED_INTERVAL)
    orders = Order.objects.filter(
        status__in=['not_confirmed', 'checking'],
        created_on__lte=offset
    ).order_by('created_on')

    return {'orders':orders}
