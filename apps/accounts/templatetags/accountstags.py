# coding: utf-8
import re
import datetime
from datetime import timedelta
from django import template
from django.template import Library, Node, TemplateSyntaxError
from django.template.defaultfilters import striptags
from apps.core.helpers import get_object_or_None
from apps.accounts.models import TimeNDay
from django.db.models import Q, get_model

register = Library()

class GetTimeDayNode(Node):
    def __init__(self, user, day, varname):
        self.user = user
        self.day = day
        self.varname = varname

    def render(self, context):
        user = self.user.resolve(context, ignore_failures=True)
        day = self.day.resolve(context, ignore_failures=True)
        if user.schedule:
            timenday = user.schedule.days.filter(weekday=day)
            context[self.varname] = timenday[0] if timenday else None
        return ''

@register.tag
def get_timeday(parser, tokens):
    bits = tokens.contents.split()
    if len(bits) != 5:
        raise TemplateSyntaxError(
               "get_timeday user day as varname")
    if bits[3] != 'as':
        raise TemplateSyntaxError, "the second argument must be 'as'"
    user = parser.compile_filter(bits[1])
    day = parser.compile_filter(bits[2])
    varname = bits[4]
    return GetTimeDayNode(user, day, varname)
