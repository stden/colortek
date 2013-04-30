import re
from itertools import chain
from datetime import datetime
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from apps.sms.utils import SMSDirect, SmsTwo, DiSMS
# Create your models here.
import logging
logger = logging.getLogger(__name__)

f = lambda x: (x,x)
SMS_PROVIDERS = map(f, settings.SMS_PROVIDERS)
SMS_STATUS_DELIVERY=(
    ('0', _("delivered")),
    ("1", _("not delivered")),
    ("2", _("unknown")),
    ("3", _("blacklisted")),
    ("4", _('invalid phone number')),
    ("5", _("invalid short-phone number")),
    # DISMS status extension
    ("6", _("Queued")),
    ("7", _("Sent")),
)

class SMSLogger(models.Model):
    mid = models.CharField(_("MID"), max_length=512)
    created_on = models.DateTimeField(default=datetime.now(), auto_now_add=True,
        verbose_name=_('created on'))
    updated_on = models.DateTimeField(default=datetime.now(), auto_now=True,
        verbose_name=_('updated on'))
    submited = models.DateTimeField(blank=True, null=True, verbose_name=_("submited"))
    status = models.CharField(_("Status Message"), choices=SMS_STATUS_DELIVERY, default="2", max_length=10)
    text = models.CharField(_("Text message"), max_length=512, blank=True)
    phone = models.CharField(_("Phone"), max_length=20)
    provider = models.CharField(_("SMS Provider"), max_length=15,
        choices=SMS_PROVIDERS,
        default=settings.SMS_PROVIDERS[0])
    resend = models.BooleanField(_("Resend?"), default=False)
    resend_count = models.PositiveSmallIntegerField(_("Resend count"), default=0)

    def __unicode__(self):
        f = lambda x,y: [x in i for i in y]
        _status = dict(SMS_STATUS_DELIVERY)
        if self.status in _status:
            status = _status[self.status]
        else:
            status = unicode(_("unknown [%(status)s]") % {'status': self.status})
        return "%(mid)s %(phone)s [%(status)s]" % {
            'mid': self.mid,
            'phone': self.phone,
            'status': status,
        }

    def send_message(self):
        message = unicode(self.text)
        if self.provider == 'smsdirect':
            sms = SMSDirect()
            mid = sms.submit_message(message, self.phone, reload=True)
            if hasattr(mid, 'http_error'):
                self.mid = None
                if mid == '900':
                    self.status = '3'
                elif mid == '300':
                    self.status = '4'
                elif mid == '400':
                    self.status = '5'
                else:
                    self.status = '2'
                    self.resend = True
                    self.resend_count += 1
                    self.save()
            else:
                if mid.isdigit():
                    self.mid = mid
                    self.resend = False
                    self.save()
                else:
                    #message have not send
                    self.resend = True
                    self.resend_count += 1
                    self.save()
            #status = sms.status
            #self.status = status
            self.save()
        elif self.provider == 'smstwo':
            sms = SmsTwo(user=settings.SMS_TWO_USER,
                            password=settings.SMS_TWO_PASSWORD)
            sms.send_message(phone=self.phone, message=message)
            response = sms._response.body #read()
            mid = re.findall(re.compile(r'Message_ID=(\d+)', re.U), response)
            mid = mid[0] if len(mid) else mid
            logger.info("recieve response from server: %s" % response)
            if mid:
                self.mid = mid
                self.resend = False
                self.save()
            else:
                self.resend = True
                self.resend_count += 1
                self.save()
        elif self.provider == 'disms':
            sms = DiSMS(user=settings.DI_SMS_USER,
                password=settings.DI_SMS_PASSWORD)
            sms.send_message(phone=self.phone, message=message)
            if hasattr(sms, 'last_id'):
                self.mid = sms.last_id
            else:
                self.resend = True
                self.resend_count += 1
                self.save()
        return self

    def update_status(self):
        if self.provider == 'smsdirect':
            c = SMSDirect()
            status = c.get_status_message(mid=self.mid)
            if status and not hasattr(c, 'http_error'):
                self.status = status \
                    if status in chain(*SMS_STATUS_DELIVERY) else '2'
            elif hasattr(c, 'http_error'):
                if status == '900':
                    self.status = 3
                elif status == '300':
                    self.status = '4'
                elif status == '401':
                    self.status = '4'
                elif status == '-1':
                    self.status = '2'
            self.save()
        elif self.provider == 'smstwo':
            c = SmsTwo(user=settings.SMS_TWO_USER, password=settings.SMS_TWO_PASSWORD)
            raw_status = c.sms_status2(mid=self.mid)
            status = re.findall(re.compile(r'Status: (\w+)', re.U|re.M|re.I), raw_status)
            status = status[0] if len(status) else 'unknown'
            if status == 'unknown':
                self.status = '2'
            elif status == 'delivered':
                self.status = '0'
            elif status == 'not delivered':
                self.status = '1'
            else:
                c.status = 'unknown'
            self.save()
        elif self.provider == 'disms':
            c = DiSMS()
            status = c.get_status(smsid=self.mid)
            if status == '1':
                self.status = '6'
            elif status == '1':
                self.status = '7'
            elif status == '2':
                self.status = '1'  # not delivered
            elif status == '3':
                self.status = '0'  # delivered
            self.save()
        return self

    class Meta:
        verbose_name = _("SMS Logger")
        verbose_name_plural = _("SMS Logger")
        #unique_together = (('mid', 'provider',), )
