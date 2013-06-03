# -*- coding: utf-8 -*-
import caching.base
from django.db import models
from django.db.models import Q
from django.conf import settings
from apps.core.managers import AbstractManager



class ItemManager(AbstractManager):
    pass


class AddonManager(AbstractManager):
    pass

class OrderManager(models.Manager):
    def get_query_set(self):
        super_class = super(OrderManager, self)
        return super_class.get_query_set().extra(select={
            'real_commission':'(cost*commission)'
            },
        )

