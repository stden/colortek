from apps.core.helpers import (
    render_to, make_http_response, model_json_encoder,
    render_to_json, get_object_or_None,
)
from apps.core.decorators import login_required_json
from django.contrib.auth.models import User
from apps.accounts.models import ContactPhone, ContactPhoneType


@login_required_json
@render_to_json(content_type='application/json')
def phones(request):
    phones = request.user.phones.all()
    return {
        'phones': phones
    }


@login_required_json
@render_to_json(content_type='application/json')
def phone_types(request):
    return {'types': ContactPhoneType.objects.all()}
