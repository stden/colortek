#coding: utf-8
from django import forms
from django.db import models
from django.db.models import Q,F
from django.contrib import admin
from apps.pages.models import Page, TextBlock
from django.utils.translation import ugettext_lazy as _

class PageAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'title', 'url', 'get_text', 'is_published')
    list_editable = ('title', 'url', 'is_published',)

    def get_text(self, obj):
        return obj.text[:50] if len(obj.text) > 50 else obj.text
    get_text.short_description = _("text")
    get_text.allow_tags = True

    class Media:
        js = (
            '/media/js/tiny_mce/tiny_mce_src.js',
            '/media/js/textareas_.js',
        )

admin.site.register(Page, PageAdmin)

class TextBlockAdmin(admin.ModelAdmin):
    list_display = ('codename', 'title', 'content' )
  
#admin.site.register(TextBlock, TextBlockAdmin)
