from datetime import datetime, timedelta

from apps.geo.models import City
from apps.core.helpers import get_object_or_None

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings

from uuid import uuid1
from decimal import Decimal


# Create your models here.
class PostType(models.Model):
    title = models.CharField(_("title"), max_length=128)
    service = models.ForeignKey('catalog.Service',
        related_name='post_type_service_set',
        default=1,
        verbose_name=_('service')
    )
    @property
    def posts(self):
        return self.post_type_set

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _("Type")
        verbose_name_plural = _("Types")


class Post(models.Model):
    type = models.ForeignKey(
        PostType, related_name='post_type_set',
        verbose_name=_("type")
    )
    title = models.CharField(
        _("title"), help_text=_("Post title"),
        max_length=256
    )
    content = models.TextField(
        _("content"), help_text=_("Post content")
    )
    announce = models.CharField(
        _("announce"), help_text=_("Post announce"),
        max_length=512
    )
    image = models.ImageField(
        _("post image"),
        upload_to=lambda s, fn: ("post/%s/%s" % (s.type.id, fn)),
        blank=True, null=True,
        max_length=256
    )
    link = models.CharField(
        _("inner link"), max_length=1024,
        help_text=_("link for service menu item"),
        blank=True, null=True
    )
    service = models.ForeignKey(
        User, related_name='post_service_set',
        blank=True, null=True,
        verbose_name=_("service")
    )
    is_approved = models.BooleanField(
        _('is approved?'), default=False
    )
    created_on = models.DateTimeField(
        _('created on'), auto_now=True,
        default=datetime.now
    )
    updated_on = models.DateTimeField(
        _('updated on'), auto_now_add=True,
        default=datetime.now
    )
    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
