from apps.core.helpers import (
    render_to, make_http_response, model_json_encoder,
    get_object_or_None
)
from apps.geo.models import City, Subway, GPos
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required


get_int_or_zero = lambda x: int(x) if (
    x.isdigit() if isinstance(x, basestring) else x
) else 0

@render_to('index.html')
def city_set(request, city_pk):
    city = get_object_or_404(City, pk=get_int_or_zero(city_pk))
    if request.session.get('city', None) != city.pk:
        request.session['city'] = city.pk
        request.session['city_title'] = city.title
        request.session.save()
    return {'redirect': request.META.get('HTTP_REFERER', '/')}


@render_to('metro.html')
def subway_widget(request, city_pk):
    city = get_object_or_404(City, pk=city_pk)
    return {'city': city}


@login_required
@render_to('accounts/set_coordinates.html')
def position_delete(request, pk):
    position = get_object_or_404(GPos, pk=pk)
    position.delete()
    return {'redirect': 'accounts:set-coordinates'}
