# coding: utf-8
from decimal import Decimal
from pytils import numeral

from django.conf import settings
from django.db.models.signals import post_save, pre_save

from apps.catalog.models import (
    Vote, BonusTransaction, Order, OrderContainer, MailCode,)
from apps.core.helpers import get_object_or_None
from apps.sms.models import SMSLogger
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.template.loader import render_to_string

from models import ORDER_STATUSES

from apps.core.async_send_mail import send_mail as async_send_mail


def vote_pre_save_action(instance, **kwargs):
    if instance.item:
        instance.item.reload_mean(save=True)
    return instance


def vote_post_save_action(instance, **kwargs):
    if instance.is_approved:
        transaction = BonusTransaction.objects.get_or_create(
            client=instance.client,
            order=instance.order,
            amount=Decimal(str(settings.BONUS_PER_VOTE_AMOUNT)),
            description='vote %s up' % instance.pk
        )
        transaction[0].client.reload_bonus_score(rebuild=True)
        transaction[0].client.save()
    return instance


def order_post_save_action(instance, **kwargs):
    bonus_rate = settings.DEFAULT_BONUS_RATE
    bonus_threshold = settings.DEFAULT_BONUS_RATE_THRESHOLD
    # do not proceed offline orders
    if not instance.client:
        return instance

    invites = instance.client.invite_reciever_user_set.filter(
        is_expired=False, is_verified=True
    ).order_by('id')  # order by first invite initiated

    if instance.status == 'rejected':
        bonuses = instance.bonus_order_set.filter(amount__lt=0)
        bonuses.delete()
        if instance.client:
            instance.client.reload_bonus_score(rebuild=True)

    if instance.status == 'approved':
        mail_code = MailCode()
        mail_code.save()
        emails = instance.container.owner.get_emails()
        phone = instance.container.owner.phone
        link = reverse('catalog:service-orders')
        async_send_mail(
                        unicode(_(u"Поступил новый заказ")),
                        render_to_string(settings.NEW_ORDER_MESSAGE_TEMPLATE_NAME,
                {'link': link, 'object': order, 'order_statuses': ORDER_STATUSES,
                'site_url': settings.SITE_URL,
                 }),
                        settings.EMAIL_FROM,
                        emails, fail_silently=True
                    )

        async_send_mail(
            subject=unicode(_(u"Поступил новый заказ")),
            body=render_to_string(settings.NEW_ORDER_MESSAGE_TEMPLATE_NAME,
    {'link': link, 'object': instance, 'order_statuses': ORDER_STATUSES,
    'site_url': settings. SITE_URL,
    'refuse_url': reverse_lazy('catalog:update_order_status',
                     kwargs=dict(pk=instance.pk, status='rejected')),
     'accept_url': reverse_lazy('catalog:update_order_status',
                     kwargs=dict(pk=instance.pk, status='finished')),
     'mail_code': mail_code,
     }),
            from_email=settings.EMAIL_FROM,
            recipient_list=emails,
        )
        amount = instance.cost
        amount_curr = numeral.choose_plural(int(round(float(str(amount)))), (u"рубль", u"рубля", u"рублей"))
        sms = SMSLogger.objects.create(
            provider='disms',
            text=settings.NEW_ORDER_SMS % {
                'time': instance.created_on.strftime("%H:%M"),
                'amount': "%s %s" % (amount, amount_curr)
            },
            phone=phone
        )
        sms.send_message()
        sms.save()

        amount_bonus = (
                instance.cost / Decimal(str(bonus_threshold)) *
                Decimal(str(bonus_rate))
        )
        if instance.client:
            user_sms = SMSLogger.objects.create(
                provider='disms',
                text=settings.USER_ORDER % {
                    'amount': amount_bonus,
                },
                phone=instance.client.phone
            )
            user_sms.send_message()
            user_sms.save()

    if instance.status == 'processed':
        # send votes
        for vote in instance.votes.all():
            if vote.is_send:
                continue

            link = settings.SITE_URL + reverse(
                'catalog:order-vote', args=(vote.sid,)
            )
            email = vote.client.email
            company = vote.order.container.owner.service_name
            message = unicode(settings.VOTE_MESSAGE % {
                'link': link,
                'company': company
            })

            async_send_mail(
                subject=unicode(_("Please vote for your order")),
                # message=unicode(settings.VOTE_MESSAGE % {
                #    'link': link,
                #    'company': company
                # }),
                body=message,
                from_email=settings.EMAIL_FROM,
                recipient_list=[email, ],
                fail_silently=True
            )
            # if not vote.is_send and vote.client.phone and settings.SEND_VOTE_SMS_ACTIVE:
            #    sms = SMSLogger.objects.create(
            #        provider='disms', text=unicode(message), phone=vote.client.phone
            #    )
            #    sms.send_message()

            vote.is_send = True
            vote.save()

        # create bonuses
        # only for authenticated users
        # saving bonus transaction

        total_price = (instance.cost - instance.discount)

        if instance.client:
            amount = (
                total_price / Decimal(str(bonus_threshold)) *
                Decimal(str(bonus_rate))
            )
            kw = dict(
                client=instance.client,
                order=instance,
                amount=amount,
                description="bonus up"
            )
            bonus_transaction = BonusTransaction.objects.filter(**kw)
            if bonus_transaction:
                bonus_transaction[0].save()
                bonus_transaction[0].client.reload_bonus_score(rebuild=True)
            else:
                kw.update({
                    'is_processed': False,
                    'is_discount': False,
                })
                bonus_transaction = BonusTransaction.objects.create(**kw)

        if instance.client:
            # initial
            if settings.FIRST_USER_ORDER_BONUS_ENABLE:
                kw = {
                    'client': instance.client,
                    'amount': Decimal(str(settings.FIRST_ORDER_BONUS)),
                    'description': 'first %s user bonus' % instance.client.pk
                }
                transaction = BonusTransaction.objects.filter(**kw)
                if not transaction:
                    transaction = BonusTransaction.objects.create(**kw)
                    phone = instance.client.phone

                    bonus_amount = (
                        total_price / Decimal(str(bonus_threshold)) *
                        Decimal(str(bonus_rate))
                    )

                    sms = SMSLogger.objects.get_or_create(
                        provider='disms',
                        text=settings.FIRST_USER_ORDER % {
                            'amount': settings.FIRST_ORDER_BONUS,
                            'bonus_amount': bonus_amount
                        },
                        phone=phone
                    )
                    sms[0].send_message()
                    sms[0].save()
                else:
                    transaction = transaction[0]
                transaction.client.save()
                transaction.client.reload_bonus_score(rebuild=True)

    if invites:
        count = instance.client.orders.count()
        if count == 1:
            sender = invites[0].sender  # use only first sender
            # invited
            transaction = BonusTransaction.objects.filter(
                client=sender,
                amount=Decimal(str(settings.BONUS_PER_INVITE_ORDER)),
                description='invited %s user' % instance.client.pk
            )

            if not transaction:
                transaction = BonusTransaction.objects.create(
                    client=sender,
                    amount=Decimal(str(settings.BONUS_PER_INVITE_ORDER)),
                    description='invited %s user' % instance.client.pk
                )
            else:
                transaction = transaction[0]
            transaction.client.save()
            transaction.client.reload_bonus_score(rebuild=True)
    #
    return instance


def order_pre_save_action(instance, **kwargs):
    instance.real_commission = instance.cost * instance.commission
    if instance.pk:
        instance.reload_total_price(commit=False)

    if instance.status == 'paid':
        # saving paid
        instance.is_paid = True
    return instance


def order_container_pre_save_action(instance, **kwargs):
    instance.reload_price(commit=False)
    return instance

def bonus_transaction_post_save(instance, **kwargs):
    if not instance.is_processed:
        instance.client.reload_bonus_score(rebuild=True)
        instance.client.save()
        # instance.client.bonus_score += instance.amount
        # instance.client.save()

def setup_signals():
    pre_save.connect(vote_pre_save_action, sender=Vote)
    post_save.connect(vote_post_save_action, sender=Vote)
    post_save.connect(order_post_save_action, sender=Order)
    pre_save.connect(order_pre_save_action, sender=Order)
    pre_save.connect(order_container_pre_save_action, sender=OrderContainer)
    # post_save.connect(bonus_transaction_post_save, sender=BonusTransaction)
