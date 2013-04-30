#!/usr/bin/env python
import lib
from apps.catalog.models import Vote
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from apps.sms.models import SMSLogger
from django.core.urlresolvers import reverse
from django.conf import settings


def update_votes(votes):
    for vote in votes:
        link = settings.SITE_URL + reverse(
            'catalog:order-vote', args=(vote.sid, )
        )
        email = vote.client.email
        company = vote.order.container.owner.service_name
        message = unicode(settings.VOTE_MESSAGE % {
            'link': link,
            'company': company
        })

        send_mail(
            subject=unicode(_("Please vote for your order")),
            #message=unicode(settings.VOTE_MESSAGE % {
            #    'link': link,
            #    'company': company
            #}),
            message=message,
            from_email=settings.EMAIL_FROM,
            recipient_list=[email, ]
        )
        
        #if vote.client.phone:
        #    sms = SMSLogger.objects.create(
        #        provider='disms', text=unicode(message), phone=vote.client.phone
        #    )
        #    sms.send_message()

        vote.is_send = True
        vote.save()

if __name__ == '__main__':
    votes = Vote.objects.filter(is_send=False)
    update_votes(votes)
