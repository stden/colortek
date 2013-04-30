# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import admin
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from apps.blog.adminforms import (
    PostAdminForm
)
from apps.blog.models import (
    Post, PostType
)


class MediaAdmin(object):
    class Media:
        js = (
            '/media/js/tiny_mce/tiny_mce.js',
            '/media/js/textareas_.js',
        )

class PostAdmin(admin.ModelAdmin, MediaAdmin):
    list_display = (
        'title', 'get_announce',
        'created_on', 'updated_on',
        'is_approved'
    )
    form = PostAdminForm

    def get_announce(self, obj):
        return mark_safe(obj.announce)
    get_announce.short_description = _("Announce")
    get_announce.allow_tags = True


class PostTypeAdmin(admin.ModelAdmin):
    list_display = ('title', 'service', )


admin.site.register(Post, PostAdmin)
admin.site.register(PostType, PostTypeAdmin)
