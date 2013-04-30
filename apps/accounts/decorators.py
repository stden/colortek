# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from apps.accounts.models import Invite, ContactPhone, ContactEmail
from apps.core.helpers import get_object_or_None
from django.conf import settings

from datetime import datetime, timedelta


def partner_required(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_partner:
            return func(request, *args, **kwargs)
        return redirect('core:blockage')
    return wrapper


def user_fields_required(fields):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            for field in fields:
                if getattr(request.user, field) is None:
                    return redirect('core:fields-required')
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def check_invite(sid):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            now = datetime.now()
            secure_id = kwargs[sid]
            invite = get_object_or_None(
                Invite, sid__iexact=secure_id, expire_date__gte=now
            )
            if not invite:
                return redirect('core:ufo')
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def phone_owner(field):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            pk = kwargs[field]
            phone = get_object_or_None(ContactPhone, pk=pk)
            if request.user == phone.user if hasattr(phone, 'user') else -1:
                return func(request, *args, **kwargs)
            return redirect('core:blockage')
        return wrapper
    return decorator
    
def email_owner(field):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            pk = kwargs[field]
            email = get_object_or_None(ContactEmail, pk=pk)
            if request.user == email.user if hasattr(email, 'user') else -1:
                return func(request, *args, **kwargs)
            return redirect('core:blockage')
        return wrapper
    return decorator    


def verified_required(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_verified:
            return redirect('core:blockage')
        return func(request, *args, **kwargs)
    return wrapper

def prevent_bruteforce(func):
    def wrapper(request, *args, **kwargs):
        if request.session.get(
            'brute_force_iter', 0
        ) > settings.BRUTEFORCE_ITER:
            # should login bastards
            raise Http404("fsck.you!")
        return func(request, *args, **kwargs)
    return wrapper
