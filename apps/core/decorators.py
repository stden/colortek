# coding: utf-8
import re
from apps.core.helpers import generate_safe_value, get_object_or_None
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

def check_allowed(*args):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            for key in args:
                try:
                    value = getattr(settings, key)
                    if not value:
                        return HttpResponseRedirect(reverse('url_blockage'))
                except:
                    pass
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

def void_xhr(func):
    def wrapper(request, *args, **kwargs):
        if 'type' in kwargs:
            type = kwargs['type']
            if type == 'void':
                response = HttpResponse()
                response['Content-Type'] = 'text/javascript'
                response.write('[]')
        return func(request, *args, **kwargs)
    return wrapper

def void_view(type, field):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if field in kwargs:
                if kwargs[field] == type:
                    return HttpResponseRedirect(reverse('url_index'))
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

def validate_get_params(parse_dict):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            request._safe_GET = {}
            safe_value = None
            for key in parse_dict.keys():
                value = request.GET.get(key, None)
                safe_value = generate_safe_value(value, parse_dict[key])
                if safe_value is not None:
                    request._safe_GET.update({key: safe_value})
            if request._safe_GET:
                request.SAFE_GET = request._safe_GET
            delattr(request, '_safe_GET')
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

def login_required_json(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated():
            return func(request, *args, **kwargs)
        response = HttpResponse()
        response['Content-Type'] = 'text/javascript'
        response.write('{"success": false, "error": "login requried"}')
        return response
    return wrapper
