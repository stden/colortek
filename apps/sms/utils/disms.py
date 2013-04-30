import os
import sys
import urllib
import urllib2
from django.conf import settings
from grab import Grab, GrabError
from hashlib import md5

FROM = settings.SMS_FROM


class DiSMS(object):
    def __init__(self, user=settings.DI_SMS_USER,
                 password=settings.DI_SMS_PASSWORD):
        self.user = user
        self.password = password
        self.errors = {}

    def forge_request(self, ta='pv', type='2', **kwargs):
        """ ta - type of opperation (required):
                pv - single sms message
                bc - group sms message delivery
                ds - get delivery status
        """
        md5_fields = [
            'u', 'ta', 'last', 'c', 'slid',
            'to', 'from', 'type', 'password'
        ]

        g = Grab()
        data = {
            'u': self.user,
            'password': self.password,
            'ta': ta,
            'type': type,
            'from': settings.SMS_FROM,
            'enc': 'cp1251',
        }

        url = settings.DI_SMS_URL
        if 'frm' in kwargs:
            data.update({'from': kwargs['frm']})
            del kwargs['frm']

        data.update(kwargs)

        # calculating md5 to commit request
        md5_string = ''
        for f in md5_fields:
            md5_string += str(data[f]) if f in data else ''
        md5_hash_string = md5(md5_string).hexdigest()
        # deleting unecessary fields
        del data['password']
        data.update({'md5': md5_hash_string})

        post = urllib.urlencode(data)
        #request = urllib2.Request(url, post)
        #grab implementation
        g.setup(post=data)
        try:
            self._response = g.go(url)
            body = self._response.body.replace('\n', '')
            # proceed reply
            if 'err' in body.lower():
                self.errors.update({
                    'code': body[4:],
                    'msg': ''
                })
            elif 'ok' in body.lower():
                self.last_id = body[3:]
                self.errors.clear()
            else:
                self.errors.update({'code': '-1', 'msg': 'unknown error'})
        except GrabError, e:
            self.http_error = {
                'code': e[0],
                'content': e[1]
            }
            self._response = None
        #urllib implementation
        #try:
        #    response = urllib2.urlopen(request)
        #    self._response = response
        #    if hasattr(self, 'http_error'):
        #        delattr(self, 'http_error')
        #except urllib2.URLError, e:
        #    self.http_error = {
        #        'code': e.code,
        #        'content': e.read()
        #    }
        return self._response

    def send_message(self, phone, message, frm=FROM, flash=0):
        frm = frm[:11] if len(frm) > 11 else frm
        if isinstance(message, unicode):
            message = message.encode('cp1251')
        else:
            message = message.decode('utf-8').encode('cp1251')
        self.forge_request(to=phone, msg=message, frm=frm)

    def get_status(self, smsid):
        self.forge_request(ta='ds', slid=smsid)
        body = self._response.body.replace('\n', '')
        return body
        # what's next?
