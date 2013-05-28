# coding: utf-8
#
import re
import os
from django.conf import settings
from django.shortcuts import (
    render_to_response, get_object_or_404 as _get_object_or_404,
    redirect)
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _, ugettext as tr
from django.template.loader import render_to_string
from django.core.exceptions import ImproperlyConfigured

from django.http import Http404
from datetime import datetime, time, date
import simplejson as json


def get_top_object_or_None(Object, *args, **kwargs):
    if hasattr(Object, 'objects'):
        obj = Object.objects.filter(*args, **kwargs)
    else:
        obj = Object.filter(*args, **kwargs)
    if obj:
        return obj[0]
    return None


def get_object_or_None(Object, *args, **kwargs):
    try:
        return _get_object_or_404(Object, *args, **kwargs)
    except (Http404, MultipleObjectsReturned):
        return None


def get_object_or_404(Object, *args, **kwargs):
    """Retruns object or raise Http404 if it does not exist"""
    try:
        if hasattr(Object, 'objects'):
            return Object.objects.get(*args, **kwargs)
        elif hasattr(Object, 'get'):
            return Object.get(*args, **kwargs)
        else:
            raise Http404("Giving object has no manager instance")
    except (Object.DoesNotExist, Object.MultipleObjectReturned):
        raise Http404("Object does not exist or multiple object returned")


def get_content_type(Object):
    """
    works with ModelBase based classes, its instances
    and with format string 'app_label.model_name', also supports
    sphinx models and instances modification
    source taken from warmist helpers source
    retrieves content_type or raise the common django Exception
    Examples:
    get_content_type(User)
    get_content_type(onsite_user)
    get_content_type('auth.user')
    """

    if callable(Object):  # class
        model = Object._meta.module_name
        app_label = Object._meta.app_label
        #model = Object.__name__.lower()
        #app_label = (x for x in reversed(
        #    Object.__module__.split('.')) if x not in 'models').next()

    elif hasattr(Object, 'pk'):  # class instance
        if hasattr(Object, '_sphinx') or hasattr(Object, '_current_object'):
            model = Object._current_object._meta.module_name
            app_label = Object._current_object._meta.app_label
            #app_label = (x for x in reversed(
            #    Object._current_object.__module__.split('.')) \
            #if x not in 'models').next()
            #model = Object._current_object.__class__.__name__.lower()
        else:
            app_label = Object._meta.app_label
            model = Object._meta.module_name
            #app_label = (x for x in reversed(Object.__module__.split('.')) \
            #if x not in 'models').next()
            #model = Object.__class__.__name__.lower()
    elif isinstance(Object, basestring):
        app_label, model = Object.split('.')
    ct = ContentType.objects.get(app_label=app_label, model=model)
    return ct


def get_content_type_or_None(Object):
    try:
        return get_content_type(Object)
    except:
        return None


def get_content_type_or_404(Object):
    try:
        return get_content_type(Object)
    except:
        raise Http404


def get_form(app_label, form_name):
    """ retrieve form within app_label and form_name given set"""
    pass


def ajax_response(dt):
    _errors = []
    if 'errors' in dt:
        for key in errors.keys():
            _errors.append({'key': key, 'msg': errors[key]})
        dt.update({'errors': _errors})
    dt.update({'status': 200})
    return dt


def generate_safe_value(value, regex):
    if isinstance(regex, str):
        regex = re.compile(regex, re.U | re.I)
    match = regex.match(value or '')
    if match:
        return match.group()
    return None


def make_http_response(**kw):
    response = HttpResponse(status=kw.get('status', 200))
    response['Content-Type'] = kw.get('content_type', 'text/plain')
    if 'content' in kw:
        response.write(kw['content'])
    return response


def make_response(type='json', **kw):
    response = HttpResponse(status=kw.get('status', 200))
    if type in ('json', 'javascript', 'js'):
        response['Content-Type'] = 'text/javascript'
    else:
        response['Content-Type'] = 'text/plain'
    return response


def ajax_form_errors(errors):
    """ returns form errors as python list """
    errs = [{'key': k, 'msg': unicode(errors[k])} for k in errors.keys()]
    #equivalent to
    #for k in form.errors.keys():
    #    errors.append({'key': k, 'msg': unicode(form.errors[k])})
    return errs


def paginate(Obj, page, **kwargs):
    from django.core.paginator import InvalidPage, EmptyPage
    from apps.core.diggpaginator import DiggPaginator as Paginator
    #from django.core.paginator import Paginator
    pages = kwargs['pages'] if 'pages' in kwargs else 20
    if 'pages' in kwargs:
        del kwargs['pages']
    paginator = Paginator(Obj, pages, **kwargs)
    try:
        objects = paginator.page(page)
    except (InvalidPage, EmptyPage):
        objects = paginator.page(1)
    objects.count = pages  # objects.end_index() - objects.start_index() +1
    return objects


def model_json_encoder(obj, **kwargs):
    from django.db.models.base import ModelState
    from django.db.models import Model
    from django.db.models.query import QuerySet
    from decimal import Decimal
    from django.db.models.fields.files import ImageFieldFile
    from django import forms
    from django.utils.functional import Promise
    is_human = kwargs.get('parse_humanday', False)
    if isinstance(obj, QuerySet):
        return list(obj)
    elif isinstance(obj, Model):
        dt = obj.__dict__
        #obsolete better use partial
        fields = ['_content_type_cache', '_author_cache', '_state']
        for key in fields:
            if key in dt:
                del dt[key]
        #normailize caches
        disable_cache = kwargs['disable_cache'] \
            if 'disable_cache' in kwargs else False

        # disable cache if disable_cache given
        for key in dt.keys():
            if '_cache' in key and key.startswith('_'):
                if not disable_cache:
                    dt[key[1:]] = dt[key]
                    #delete cache
                    del dt[key]
            if disable_cache and '_cache' in key:
                del dt[key]

        #delete restriction fields
        if kwargs.get('fields_restrict'):
            for f in kwargs.get('fields_restrict'):
                if f in dt:
                    del dt[f]
        #make week more humanic
        if is_human and 'week' in dt:
            dt['week'] = unicode(humanday(dt['week']))
        return dt
    elif isinstance(obj, ModelState):
        return 'state'
    elif isinstance(obj, datetime):
        return [
            obj.year, obj.month, obj.day,
            obj.hour, obj.minute, obj.second,
            obj.isocalendar()[1]
        ]
    elif isinstance(obj, date):
        return [obj.year, obj.month, obj.day]
    elif isinstance(obj, time):
        return obj.strftime("%H:%M")
    elif isinstance(obj, ImageFieldFile):
        return obj.url if hasattr(obj, 'url') else ''
    elif isinstance(obj, forms.ModelForm) or isinstance(obj, forms.Form):
        _form = {
            'data': obj.data if hasattr(obj, 'data') else None,
            'instance': obj.instance if hasattr(obj, 'instance') else None,
        }
        if obj.errors:
            _form.update({'errors': obj.errors})
        return _form
    elif isinstance(obj, Promise):
        return unicode(obj)
    #elif isinstance(obj, Decimal):
    #    return float(obj)
    return obj


def get_model_instance_json(Obj, id):
    instance = get_object_or_None(Obj, id=id)
    response = make_http_response(content_type='text/javascript')
    if not instance:
        response.write(json.dumps({
            'success': False,
            'error': unicode(_("Not found")),
        }, default=model_json_encoder))
        return response
    response.write(json.dumps({
        'success': True,
        'instance': instance,
    }, default=model_json_encoder))
    return response


def create_path(path):
    try:
        os.stat(path)
    except OSError, e:
        if e.errno == 2:
            os.makedirs(path)
        else:
            pass
    return path


def get_safe_fields(lst, Obj):
    """ excludes fields in given lst from Object """
    return [
        field.attname for field in Obj._meta.fields
        if field.attname not in lst
    ]


#decorators
def render_to_json(content_type='application/json'):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            dt = func(request, *args, **kwargs)
            response = make_http_response(content_type=content_type)
            response.write(json.dumps(dt, default=model_json_encoder))
            return response
        return wrapper
    return decorator


def render_to(template, allow_xhr=False, content_type='text/html'):
    _content_type = content_type
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            response = make_http_response(content_type='application/json')
            dt = func(request, *args, **kwargs)
            if not isinstance(dt, dict):
                raise ImproperlyConfigured("render_to should take dict instance not %s" % type(dt))
            # overrides
            tmpl = dt.get('_template', template)
            content_type = dt.get('_content_type', _content_type)

            force_ajax = request.META.get('HTTP_X_FORCE_XHTTPRESPONSE', None)
            if 'redirect' in dt:
                if force_ajax:
                    response.write(json.dumps({"status": "ok"}))
                    return response

                args = dt.get('redirect-args', [])
                if args:
                    redr = reverse(dt['redirect'], args=args)
                    return redirect(redr)
                return redirect(dt['redirect'])

            if content_type.lower() == 'text/html':
                if force_ajax and allow_xhr:
                    response.write(json.dumps(dt, default=model_json_encoder))
                    return response
                return render_to_response(
                    tmpl,
                    dt,
                    context_instance=RequestContext(request))

            elif content_type.lower() == 'text/csv':
                response = make_http_response(content_type=content_type)
                response['Content-Disposition'] = 'attachment; filename="export.csv"'
                response.write(
                    render_to_string(tmpl, dt)
                )
                return response

            elif content_type.lower() in ('text/json', 'text/javascript',
                                          'application/json'):
                response = HttpResponse()
                response['Content-Type'] = content_type
                tmpl = get_template(tmpl)
                response.write(tmpl.render(Context(dt)))
                return response
            else:
                return render_to_response(
                    tmpl,
                    dt, context_instance=RequestContext(request))
        print 'TEMPLATE', template
        return wrapper
    return decorator


def get_model_content_type(Obj):
    return ContentType.objects.get(
        app_label=Obj._meta.app_label,
        model=Obj._meta.module_name)
