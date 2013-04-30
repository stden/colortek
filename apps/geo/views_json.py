from apps.core.helpers import (
    render_to, make_http_response, model_json_encoder,
    render_to_json, get_object_or_None
)
from apps.geo.models import City, Subway


@render_to_json(content_type='application/json')
def subways(request, city_pk):
    city = get_object_or_None(City, pk=city_pk)
    subways = Subway.objects.filter(
        city=city)

    return {
        'subways': subways
    }
