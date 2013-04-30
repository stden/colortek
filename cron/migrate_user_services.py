#!/usr/bin/env python
import lib
from django.db.models import F
from apps.catalog.models import Container
from apps.accounts.models import User
from django.conf import settings


def update_service(users):
    for u in users:
        Container.objects.filter(owner=u).update(service=u.service)

if __name__ == '__main__':
    users = User.objects.filter(is_partner=True)
    update_service(users)
