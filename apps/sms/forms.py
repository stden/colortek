# coding: utf-8
import re
from django import forms
from django.utils.translation import ugettext_lazy as _, ugettext as _tr
from apps.sms.utils import approve_sms_subscription, dict2xml, md5hash_generate
from django.forms.util import ErrorList
from django.conf import settings
from apps.sms.errors import RESPONSE_MESSAGES
from apps.sms.xml import make_xml

class SubscribeSMSForm(forms.Form):
    required_css_class = 'required'
    phone = forms.RegexField(regex=re.compile(r'[^\+]?([\d\- ]{11})', re.M),
        error_message=_('You have given wrong phone number'), required=True,
        help_text=('7 9xx xxx xx xx'))
    approve = forms.BooleanField(label=_('Yes, I approve'), required=True)

class UnsubscribeSMSForm(SubscribeSMSForm):
    required_css_class = 'required'

class ConfirmSMSForm(forms.Form):
    required_css_class = 'required'
    pin = forms.IntegerField(label=_('Code'),
        help_text=_('Message code you which you should recieve on you phone within several minutes'))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs['request']
            del kwargs['request']
        super(ConfirmSMSForm, self).__init__(*args, **kwargs)

    def clean_pin(self):
        value = self.cleaned_data['pin']
        req = self.request
        response = approve_sms_subscription(
            value, req.user.phone, req.META.get('REMOTE_ADDR', '127.0.0.1'))
        if not response['success']:
            response_dict = RESPONSE_MESSAGES['APPROVE_SUBSCRIPTION_MESSAGES']
            status_msg = response_dict['statusname'].get(response['statusname'], _('Unknown error'))
            error_msg = response_dict['errorreasonname'].get(response['errorreasonname'], _tr('Unknow error message'))
            error_dsc_msg = response.get('errordescription', None)
            msg = "%s\n%s\n%s" % (status_msg, error_msg, error_dsc_msg)
            raise forms.ValidationError(msg)
        else:
           self.subscription_id = response['subscriptionid']
        return value

class SubscriptionStatusNotificationForm(forms.Form):
    subscriptionid = forms.IntegerField()
    subscriptionprojectid = forms.CharField()
    subscriberid = forms.IntegerField()
    signature = forms.CharField()
    now = forms.CharField()
    subscriber_msisdn = forms.CharField()
    eventtype = forms.MultipleChoiceField(choices=(
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('APPROVED_BILLING', 'Approved billing'),
        ('REJECTED_BILLING_ATTEMPT', 'Rejected billing attempt'),
        ('REJECTED_BILLING', 'Rejected billing'),
        ('CANCELLED', 'Cancelled'),
        ('FINISHED', 'Finished'),
    ))
    subscriptionstatus = forms.MultipleChoiceField(choices=(
        ('Active', 'Active'),
        ('Renewing', 'Renewing'),
        ('Closed', 'Closed'),
        ('Cancelled', 'Cancelled'),
        ('Redelivering', 'Redelivering'),
        ('RenewingFailed', 'Renewing failed'),
        ('ApprovingFailed', 'Approving failed')
    ))
    billingiteration = forms.IntegerField()
    billingattempt = forms.IntegerField()
    country = forms.CharField(max_length=2)
    operatorid = forms.IntegerField()
    customerpricecurrency = forms.CharField(max_length=3)
    customerpriceamount = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        self.xml_response = ''
        super(SubscriptionStatusNotificationForm, self).__init__(*args, **kwargs)

    def clean(self):
        #validate security issues, check md5sum
        cd = self.cleaned_data
        subscription_project_id = cd.get('subscriptionprojectid', None)
        now = cd.get('now', None)
        signature = cd.get('signature', None)
        if not now or not signature or not subscription_project_id:
            self._errors['signature'] = ErrorList([_('Signature failed')])
            self.xml_response = make_xml({
                'StatusName': 'SECURITY_ERROR',
                'ErrorDescription': 'md5 hash validation failed, not valid md5'
            })

        md5hash = md5hash_generate(subscription_project_id, now, settings.SMS_SECRET_KEY)
        if not md5hash.hexdigest() == signature:
            data = {
                'StatusName': 'SECURITY_ERROR',
                'ErrorDescription': "MD5 hash validation failed, not valid md5"
            }
            xml_data = make_xml(data)
            msg = _('Signature failed')
            self._errors['signature'] = ErrorList([msg])
            self.xml_response = xml_data
            if 'signature' in cd:
                del cd['signature']
        else:
            xml_response = make_xml({
                'StatusName': 'REQUEST_ACCEPTED'
            })
            self.xml_response = xml_response
        return cd

class IncomeSMSForm(forms.Form):
    evtId = forms.IntegerField()
    phone = forms.CharField()
    abonentId = forms.CharField()
    country = forms.CharField(max_length=5)
    serviceNumber = forms.CharField()
    network = forms.CharField()
    networkId = forms.IntegerField()
    smsText = forms.CharField()
    EUP = forms.FloatField()
    EUPCurrency = forms.CharField()
    profit = forms.FloatField()
    profitCurrency = forms.CharField()
    now = forms.CharField()
    md5key = forms.CharField()
    test = forms.CharField(required=False)
    debug = forms.BooleanField(required=False)
    retry = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(IncomeSMSForm, self).__init__(*args, **kwargs)
        self.xml_response = None
        self.sms_text = None

    def clean(self):
        cd = self.cleaned_data
        items = {
            'service_number': cd.get('serviceNumber', None),
            'sms_text': cd.get('smsText', None),
            'country': cd.get('country', None),
            'abonent_id': cd.get('abonentId', None),
            'now': cd.get('now', None),
        }
        optional_items = {
            'retry': cd.get('retry', False),
            'debug': cd.get('debug', False),
            'test': cd.get('test', None),
        }
        #send test OK
        if optional_items['test']:
            self.xml_response = make_xml({
                'SmsText': optional_items['test']
            })
            return cd

        #check
        mapping = map(lambda x: bool(x), items.values())
        errors = [i for i in mapping if not i]
        if errors:
            xml_response = make_xml({
                'ErrorText': 'Given params is not enough to complete request'
            })
            self.xml_response = xml_response
            self._errors['md5key'] = ErrorList([_('Security issues')])
            return cd
        items['secret_key'] = settings.SMS_SECRET_KEY
        order = ['service_number', 'sms_text', 'country', 'abonent_id',
            'secret_key', 'now']
        keys = [items[i] for i in order]
        md5hash = md5hash_generate(*keys)
        if optional_items['retry']:
            md5hash.update('1')
        if optional_items['debug']:
            md5hash.update('1')
            md5hash.update(settings.SMS_DEBUG_SECRET_KEY)
        if md5hash.hexdigest() == cd.get('md5key', None):
            self.sms_text = items['sms_text']
            self.xml_response = make_xml({
                'SmsText': 'you request queued'
            })
        else:
            self.xml_response = make_xml({
                'ErrorText': 'md5key is not valid, security error'
            })
            self._errors['md5key'] = ErrorList([_('Md5key is not valid, security error')])
        return cd

