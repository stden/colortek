# -*- coding: utf-8 -*-
from apps.core.managers import UserSIDManager

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from datetime import datetime, timedelta
# your models here


class UserSID(models.Model):
    user = models.ForeignKey(User, related_name='user_sid_set')
    sid = models.CharField(_("SID"), unique=True, max_length=512)
    # additional fields ?
    expired_date = models.DateTimeField(
        _("Expires"), default=datetime.now() + timedelta(weeks=1)
    )
    expired = models.BooleanField(
        _("expired?"), default=False
    )
    created_on = models.DateTimeField(
        _("created on"), default=datetime.now,
        auto_now=True
    )
    updated_on = models.DateTimeField(
        _('updated on'), default=datetime.now,
        auto_now_add=True
    )
    objects = UserSIDManager()

    def __unicode__(self):
        return "%s [%s]" % (self.user.username, self.sid)

    class Meta:
        verbose_name = _("UserSID")
        verbose_name_plural = _("UserSIDs")
