# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import admin
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags

#from apps.catalog.adminforms import (
#    ServiceAdminForm, ContainerAdminForm)
from apps.geo.models import City, Subway, YaLink, YaType, GPos


class MediaAdmin(object):
    class Media:
        js = (
            '/media/js/tiny_mce/tiny_mce.js',
            '/media/js/textareas.js',
        )


class CityAdmin(admin.ModelAdmin):
    list_display = ("title", 'iso', 'codename', 'priority')
    list_editable = ('priority', 'codename', 'iso', )


class SubwayAdmin(admin.ModelAdmin):
    list_display = ("title", 'city', 'get_yalink')
    search_fields = ('title', 'city__title')


class YaLinkAdmin(admin.ModelAdmin):
    list_display = ('subway', 'coords', 'type')
    list_editable = ("coords", 'type')


admin.site.register(City, CityAdmin)
admin.site.register(Subway, SubwayAdmin)
admin.site.register(YaLink, YaLinkAdmin)
admin.site.register(YaType)
admin.site.register(GPos)
