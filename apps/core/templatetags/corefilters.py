# coding: utf-8
from django.template import Library
from django import template
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
import os
from django.conf import settings

register = Library()


@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except ValueError:
        return value


@register.filter(name='int')
def int_filter(value):
    try:
        return int(value)
    except ValueError:
        return None


@register.filter(name='float')
def float_filter(value):
    try:
        if isinstance(value, float):
            return value
        return float(value.replace(',', '.'))
    except ValueError:
        return None


@register.filter(name='get')
def get_filter(value, arg):
    return value.get(arg) if hasattr(value, 'get') else None


@register.filter(name='oget')
def option_get_filter(value, arg):
    try:
        for opt in value:
            if opt[0] == arg:
                return opt[1]
    except TypeError:
        return value

@register.filter(name='default_if_blank')
def default_if_blank(value, arg):
    if isinstance(value, basestring):
        return arg if value == '' else value
    return value

@register.filter(name='select_day')
def select_day(value, arg='s'):
    days = [_("Mon"), _("Tue"), _("Wed"), _("Thu"), _("Fri"), _("Sat"), _("Sun")]
    full_days = [
        _("Monday"), _("Tuesday"), _("Wednesday"),
        _("Thursday"), _("Friday"), _("Saturday"), _("Sunday")
    ]
    if arg in ('f', 'full'):
        return full_days[int(value)-1]
    return days[int(value)-1]

@register.filter(name='select_month')
def select_month(value):
    months = [
        _("January"), _("February"), _("March"), _("April"), _("May"),
        _("June"), _("July"), _("August"), _("September"), _("October"),
        _("November"), _("December")
    ]
    if isinstance(value, int):
        if value > 0 and value < 13:
            return months[int(value)-1]
    elif isinstance(value, basestring):
        if value.isdigit():
            if int(value) > 0 and int(value) < 13:
                return months[int(value)-1]
    return None

@register.filter(name='phone_split')
def phone_split(value, arg=None):
    r = (value[1:4], value[4:])
    if arg:
        return r[int(arg)]
    return r

@register.filter(name='split')
def split(value, arg):
    if isinstance(value, basestring):
        return value.split(arg)
    return value

@register.filter(name='select')
def select(value, arg):
    if isinstance(value, list) or isinstance(value, tuple):
        return value[int(arg)]
    return value

@register.filter(name='increase_rate')
def increase_rate(value, arg):
    if isinstance(value, float) or isinstance(value, int):
        return value / float(arg) / float(arg)
    elif isinstance(value, basestring):
        if value.isdigit():
            return float(value) / float(arg) / float(arg)
    return value

@register.filter(name='deliver_time')
def deliver_time(value):
    day = re.findall('(\d+)d', value)
    hour = re.findall('(\d+)h', value)
    minute = re.findall('(\d+)m', value)
    return {
        'day': "".join(day),
        'hour': "".join(hour),
        "minute": "".join(minute)
    }
    
@register.filter(name='subtract')    
def subtract(value, arg):
    return value - arg     

@register.filter(name='debug')
def debug(value):
    import ipdb
    ipdb.set_trace()
    return
