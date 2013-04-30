# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import admin
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags

from apps.accounts.models import (
    ContactPhone, ContactPhoneType, ContactEmail, Invite,
    DeliverCost, TimeNDay
)


#replace media admin with common
class MediaAdmin(object):
    class Media:
        js = (
            '/media/js/tiny_mce/tiny_mce.js',
            '/media/js/textareas.js',
        )


class ContactPhoneAdmin(admin.ModelAdmin, MediaAdmin):
    list_display = ('phone', 'type', 'user', )
    list_editable = ('type', )


class ContactPhoneTypeAdmin(admin.ModelAdmin, MediaAdmin):
    list_display = ('id', 'title', )
    list_editable = ('title', )


class ContactEmailAdmin(admin.ModelAdmin):
    list_display = ("email", 'user')


class InviteAdmin(admin.ModelAdmin):
    list_display = ('sender', 'email', 'is_verified', 'created_on')


#class DeliverCostAdmin(admin.ModelAdmin):
#    list_display = ('user', 'cost', 'min', 'max',)


admin.site.register(Invite, InviteAdmin)
admin.site.register(ContactPhone, ContactPhoneAdmin)
admin.site.register(ContactPhoneType, ContactPhoneTypeAdmin)
admin.site.register(ContactEmail, ContactEmailAdmin)
#admin.site.register(DeliverCost, DeliverCostAdmin)
admin.site.register(TimeNDay)
