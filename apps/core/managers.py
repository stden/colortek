from django.db import models
from datetime import datetime
from hashlib import sha1

from apps.core.helpers import get_object_or_None
from django.contrib.auth.models import User
from uuid import uuid1


class AbstractManager(models.Manager):
    """ marks all is_deleted=True objects as 'non existant' """
    def get_query_set(self):
        return super(AbstractManager, self).get_query_set().filter(is_deleted=False)


class UserSIDManager(models.Manager):
    def create(self, user):
        sid = uuid1().hex

        if not user:
            return None

        instance = self.model(user=user, sid=sid)
        instance.save()
        return instance

