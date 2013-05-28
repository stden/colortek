# coding: utf-8просве
from datetime import datetime, timedelta
from decimal import Decimal
from pytils import numeral

from django.conf import settings
from django.db.models.signals import post_save, pre_save

from django.template.loader import render_to_string
from django.contrib.auth.models import User
from apps.accounts.models import Verification
from apps.core.helpers import get_object_or_None
from apps.catalog.models import BonusTransaction
from apps.sms.models import SMSLogger
from django.core.mail import send_mail, EmailMultiAlternatives as EmailMulti
from django.core.urlresolvers import reverse
from django.conf import settings


def user_pre_save(instance, **kwargs):
    #if not instance.pk and instance.phone:
    #    sms = SMSLogger.objects.get_or_create(
    #        provider='disms',
    #        text=settings.USER_REGISTER_SMS,
    #        phone=instance.phone
    #    )
    #    sms[0].send_message()
    #    sms[0].save()
    #if instance.is_partner:
    #    instance.is_verified = True

    if instance.verification:
        # acts only if is_verified is False (e.g. do not affect on admin page)
        if not instance.is_verified:
            instance.is_verified = instance.verification.is_verified

    if instance.is_published and not instance.published_once:
        instance.publish_date = datetime.now()
        instance.published_once = True
    return instance


def user_post_save(instance, **kwargs):
    # register bonus
    if settings.REGISTER_BONUS_ENABLE:
            kw = dict(
                client=instance,
                amount=Decimal(str(settings.REGISTER_BONUS)),
                description='register %s up' % instance.pk
            )
            transaction = BonusTransaction.objects.filter(**kw)
            if not transaction:
                transaction = BonusTransaction.objects.create(**kw)
                instance.reload_bonus_score(rebuild=True)
    if not any ((instance.is_verified, instance.verification)):
        Verification.objects.create(user=instance)
        email = instance.email
        link = reverse('accounts:account-verify', args=(instance.verification.sid,))
        link = settings.SITE_URL + link
        subject = u"Подтверждение регистрации"
        #information = unicode(settings.REGISTER_VERIFICATION_MESSAGE % {'link': link})
        #send_mail(
        #    subject=subject,
        #    message=unicode(settings.REGISTER_VERIFICATION_MESSAGE % {'link': link}),
        #    from_email=settings.EMAIL_FROM,
        #    recipient_list=[email, ]
        #)
        information = render_to_string('mail/register.html', {
            'link': link
        })
        message = EmailMulti(subject, information, settings.EMAIL_FROM, [email])
        message.content_subtype ='html'
        message.send()

    return instance

def setup_signals():
    pre_save.connect(user_pre_save, sender=User)
    post_save.connect(user_post_save, sender=User)
