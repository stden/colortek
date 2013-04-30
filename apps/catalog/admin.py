# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import admin
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from apps.catalog.adminforms import (
    ServiceAdminForm, ContainerAdminForm, OrderAdminForm,
    VoteAdminForm
)
from apps.catalog.models import (
    Service, Container, Item, Addon, AddonList, Order,
    OrderContainer, OfflineClient, ServiceTerm,
    Category, PaymentTransaction, Special,
    ItemCategory, AddonCategory,
    #Vote stuff
    Vote, VoteItem, VoteAtom, VoteKlass, VoteLink,
    BonusTransaction
)


class MediaAdmin(object):
    class Media:
        js = (
            '/media/js/tiny_mce/tiny_mce.js',
            '/media/js/textareas.js',
        )


class ServiceAdmin(admin.ModelAdmin, MediaAdmin):
    list_display = ('title', 'codename', 'get_description', 'weight')
    list_editable = ('weight', )
    form = ServiceAdminForm

    def get_description(self, obj):
        return strip_tags(obj.description)
    get_description.short_description = _("description")
    get_description.allow_tags = True


class ContainerAdmin(admin.ModelAdmin, MediaAdmin):
    list_display = ('__unicode__', 'container', 'get_description', 'category')
    list_editable = ('category', )
    form = ContainerAdminForm

    def get_description(self, obj):
        return strip_tags(obj.description)
    get_description.short_description = _("description")


class OrderAdmin(admin.ModelAdmin, MediaAdmin):
    list_display = ('__unicode__', 'get_client', 'get_real_name', 'cost', 'is_offline' )
    form = OrderAdminForm
    # define the raw_id_fields
    #raw_id_fields = ('items', 'client', 'addons',)
    # define the related_lookup_fields
    #related_lookup_fields = {
    #    'm2m': ['items', 'addons', ],
    #    'fk': ['client'],
    #}
    def get_client(self, obj):
        return obj.get_client()
    get_client.short_description = _("client")

    def get_real_name(self, obj):
        return obj.get_client().get_real_name()
    get_real_name.short_description = _('name')

    def is_offline(self, obj):
        icon = 'yes' if obj.is_offline else 'no'
        return mark_safe(
            '<img src="/media/admin/img/icon-%s.gif" alt="%s">' % (icon, obj.is_offline)
        )
    is_offline.short_description = _('is offline')
    is_offline.allow_tags = True

class OrderContainerAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', )


class BonusTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'client', 'amount', 'order', 'is_processed',
        'is_discount', 'description'
    )


class OfflineClientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'phone', 'street', 'building', 'apartment', 'need_change',
        'get_client'
    )

    def get_client(self, obj):
        return obj.client
    get_client.short_description = _("client")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'title', 'service', 'weight')
    list_editable = ('title', 'service', 'weight',)
    list_filter = ('service', )


class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('client', 'order', 'partner', 'amount', 'payment_id')


class VoteAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'is_approved', 'is_proceeded', 'sid')
    list_editable = ('is_approved', 'is_proceeded')
    form = VoteAdminForm


class SpecialAdmin(admin.ModelAdmin):
    list_display = ('owner', 'title', 'description', 'expires')
    list_editable = ('title', )


class AbstractCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'get_title', 'title', 'threshold', 'rate', 'short_title', 'short_rate_title', 'description'
    )
    list_editable = (
        'title', 'threshold', 'rate', 'short_title', 'description', 'short_rate_title',
    )


class ItemCategoryAdmin(AbstractCategoryAdmin):
    pass


class AddonCategoryAdmin(AbstractCategoryAdmin):
    pass

admin.site.register(Service, ServiceAdmin)
admin.site.register(Container, ContainerAdmin)
admin.site.register(AddonList)
admin.site.register(Addon)
admin.site.register(Item)
admin.site.register(ItemCategory, ItemCategoryAdmin)
admin.site.register(AddonCategory, AddonCategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderContainer, OrderContainerAdmin)
admin.site.register(BonusTransaction, BonusTransactionAdmin)
admin.site.register(OfflineClient, OfflineClientAdmin)
admin.site.register(ServiceTerm)
admin.site.register(Category, CategoryAdmin)
admin.site.register(PaymentTransaction, PaymentTransactionAdmin)
admin.site.register(Special, SpecialAdmin)
#votes
admin.site.register(VoteKlass)
admin.site.register(VoteAtom)
admin.site.register(VoteItem)
admin.site.register(VoteLink)
admin.site.register(Vote, VoteAdmin)
