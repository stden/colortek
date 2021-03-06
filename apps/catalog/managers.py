DI_SMS_PASSWORD = '1233123'
SMS_DIRECT_PASSWORD = '123'
SMS_TWO_PASSWORD = '123'# -*- coding: utf-8 -*-
from django.db import models
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

