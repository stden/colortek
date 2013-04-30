#!/usr/bin/env python
import lib
from apps.catalog.models import Container
from django.conf import settings


def update_rating(containers):
    for container in containers:
        container.reload_atom_rating()
        container.reload_common_rating()

if __name__ == '__main__':
    containers = Container.objects.all() #.order_by('owner').distinct('owner')
    update_rating(containers)
