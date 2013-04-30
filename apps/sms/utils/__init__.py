# coding: utf-8
import os
from django.conf import settings
from datetime import datetime, timedelta
from hashlib import md5
from celery.task import task
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from smsdirect import SMSDirect
from smstwo import SmsTwo
from disms import DiSMS

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import logging
logger = logging.getLogger(__name__)

def md5hash_generate(*args):
    md5hash = md5()
    for arg in args:
        md5hash.update(arg)
    return md5hash

def get_value(lst):
    if len(lst) > 0:
        return lst[0]
    return None


@task
def test_celery_intervals():
    """ tests if celery intervals works correct """
    f = open(os.path.join(settings.MEDIA_ROOT, 'test_intervals'), 'a+')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    f.write('%s is written\n' % now)
    f.close()
    return 0

@task
def test_celery():
    filename = os.path.join(settings.MEDIA_ROOT, 'celery_check.txt')
    open(filename, 'w+').write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@task
def resend_failed_sms():
    """ resends sms that failed send """
    from apps.sms.models import SMSLogger
    queue = SMSLogger.objects.filter(resend=True, resend_count__lt=4)
    for sms in queue:
        sms.send_message()
    return

@task
def update_sms_statuses():
    """ updates sms status to know if we were delivered """
    from apps.sms.models import SMSLogger
    time = datetime.now() - timedelta(days=1)
    queue = SMSLogger.objects.filter(created_on__gte=time,
        resend=False, status='2') | SMSLogger.objects.filter(
        created_on__gte=time, resend=False, status=None)
    for sms in queue:
        sms.update_status()
    return
#@task
def _send_sms(message, to):
    from apps.sms.models import SMSLogger
    """ sends sms to given msisdn """
    slog = SMSLogger(phone=to, text=message, mid=None, status='2',
        provider=settings.SMS_PROVIDER)
    slog.send_message()
    """
    if settings.SMS_PROVIDER == 'smsdirect':
        sms = SMSDirect()
        message = unicode(message)
        sms.submit_message(message, to, reload=True)
        status = sms.status
        if not hasattr(sms, 'http_error'):
            slog = SMSLogger(phone=to, text=message, mid=sms.message)
            slog.save()
        del sms #fails with celery pickle
        return status
    elif settings.SMS_PROVIDER == 'smstwo':
        sms = SmsTwo(user=settings.SMS_TWO_USER, password=settings.SMS_TWO_PASSWORD)
        message = unicode(message)
        sms.send_message(phone=to, message=message)
        response = sms._response.read()
        return response
    return None #Provider not set
    """

def send_void_sms(*args, **kwargs):
    sms = SMSDirect()
    message = kwargs['message'] if 'message' in kwargs else ''
    message = unicode(message)
    if settings.DEBUG_MESSAGES:
        logger.info('sms was not send because SMS_DIRECT_ENABLE is disabled')
        logger.info('message given: %s' % message)
    return


#@task
def _send_notification(type='email', **kwargs):
    """ sends notification to user """
    kwargs.update({'fail_silently': True})
    if type == 'email':
        send_mail(**kwargs)
        return 0
    else:
        return 0

def send_void_mail(*args, **kwargs):
    if settings.DEBUG_MESSAGES:
        logger.info('no email sent, because SEND_EMAIL is disabled')
    if 'message' in kwargs:
        if settings.DEBUG_MESSAGES:
            logger.info("message: %s" % kwargs['message'])
    return

#SET SETTINGS, DISABLING SENDING NOTIFICATIONS OR ENABLING THEM
if settings.SMS_ENABLE:
    send_sms = task(_send_sms)
else:
    send_sms = lambda x,y: x
    send_sms.delay = send_void_sms

if settings.SEND_EMAIL:
    send_notification = task(_send_notification)
else:
    send_notification = lambda x: x
    send_notification.delay = send_void_mail
