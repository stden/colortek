# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from apps.banner.models import Banner


class BannerAdmin(admin.ModelAdmin):
    list_display = ("url", 'weight', 'description', 'is_active')
    list_editable = ('weight', 'description', 'is_active' )


admin.site.register(Banner, BannerAdmin)
