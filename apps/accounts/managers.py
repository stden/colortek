# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from apps.core.helpers import get_object_or_None
from django.db.models import Q
from django.db import models
from django.conf import settings
from datetime import datetime, timedelta
from uuid import uuid1

class VerificationManager(models.Manager):
    def create(self, **kwargs):
        model_class = self.model
        if 'user' in kwargs:
            if isinstance(kwargs['user'], User):
                user = get_object_or_None(self.model, pk=kwargs['user'].pk)
                if user:
                    return user
        sid = uuid1().hex
        kwargs.update({'sid': sid})
        instance = super(VerificationManager, self).create(**kwargs)
        return instance
