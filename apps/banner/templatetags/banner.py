# -*- coding: UTF-8 -*-

from django import template
from django.template.loader import render_to_string
from django.conf import settings

from apps.banner.models import Banner
from apps.core.helpers import get_object_or_None
from django.template import Library, Node, TemplateSyntaxError

register = template.Library()


@register.simple_tag
def get_banner(template='banner/banner.html', by_weight=True, count=3, random=False):
    banners = Banner.objects.filter(
        is_active=True).order_by('?' if random else '-weight')[:count]
    banner = None
    if banners:
        banner = banners[0]
        if by_weight:
            banners = Banner.objects.filter(pk__in=banners).order_by('-weight')
    return render_to_string(template, {
        'banners': banners,
        'banner': banner,
        'gs': settings
    })
