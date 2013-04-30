# coding: utf-8
from hashlib import md5
from django.conf import settings

def checksum(what):
    return md5(''.join(what)).hexdigest()

def copy_fields(instance, fields):
    new_instance = {}
    for f in fields:
        new_instance.update({
            f: getattr(instance, f) if hasattr(instance, f) else None
        })
    return new_instance

def is_valid(data):
    amount, userid, paymentid = map(
        data.get,
        ('amount', 'userid', 'paymentid')
    )
    return checksum(
        [amount, userid, paymentid, settings.DO_SECRET]
    ) == data.get('key', '')

