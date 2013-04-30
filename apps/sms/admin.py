#coding: utf-8
from django.contrib import admin
from apps.sms.models import SMSLogger
from django.utils.translation import ugettext_lazy as _

class SMSLoggerAdmin(admin.ModelAdmin):
    list_display = (
        'mid', 'phone', 'text', 'status',
        'provider', 'created_on', 'updated_on',
        #'resend', 'resend_count'
    )
    search_fields = ('phone', 'text', 'mid')
    def check_status(self, request, queryset):
        for instance in queryset:
            instance.update_status()
    check_status.short_description = _("Check status")
    actions = [check_status, ]

admin.site.register(SMSLogger, SMSLoggerAdmin)
