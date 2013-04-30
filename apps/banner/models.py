from datetime import datetime, timedelta
from django.db import models
from django.utils.translation import ugettext_lazy as _
# Create your models here.

class Banner(models.Model):
    url = models.URLField(
        _('url'), help_text=_('where should click on banner go'),
        max_length=1024
    )
    image = models.ImageField(
        _("image"), help_text=_("banner image"), blank=True, null=True,
        upload_to=lambda s, fn: ("banners/%s_%s" % (
            s.created_on.strftime('%Y%m%d_%H%M'),
            fn
        )),
        max_length=256

    )
    created_on = models.DateTimeField(
        _('created on'), auto_now=True,
        default=datetime.now
    )
    updated_on = models.DateTimeField(
        _('updated on'), auto_now_add=True,
        default=datetime.now
    )
    weight = models.PositiveIntegerField(
        _('weight'), default=0
    )
    description = models.CharField(
        _('description'), help_text=_('banner description'),
        max_length=2048, blank=True, null=True
    )
    is_active = models.BooleanField(
        _('is active?'), help_text=_('marks if banner is active'),
        default=True
    )

    class Meta:
        verbose_name = _("Banner")
        verbose_name_plural = _("Banners")
        ordering = ['-weight', ]
