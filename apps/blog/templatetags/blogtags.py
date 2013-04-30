# -*- coding: UTF-8 -*-

from django import template
from django.template.loader import render_to_string

from apps.blog.models import Post, PostType
from apps.core.helpers import get_object_or_None
from django.contrib.auth.models import User

register = template.Library()


@register.simple_tag
def blog_types(service, post=None, category=None, template='blog/include/blog_types.html'):
    types = PostType.objects.filter(service=service)
    return render_to_string(template, {
        'types': types,
        'post': post,
        'category': category
    })
