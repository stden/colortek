import os
import sys
import urllib
import urllib2
from django.conf import settings
from grab import Grab, GrabError

FROM=settings.SMS_FROM #'kotbaun'
SMS_TWO_PREFIX=settings.SMS_TWO_URL #'http://sms.spb.ru/'

class SmsTwo(object):
    def __init__(self, user=settings.SMS_TWO_USER,
        password=settings.SMS_TWO_PASSWORD):
        self.user = user
        self.password = password
        self.flash = 0

    def forge_request(self, **kwargs):
        g = Grab()
        data = {
            'user': self.user,
            'pass': self.password,
        }
        url = "%ssms.cgi" % SMS_TWO_PREFIX
        if 'url' in kwargs:
            url = '%s%s' % (SMS_TWO_PREFIX, kwargs['url'])
            del kwargs['url']
        if 'frm' in kwargs:
            data.update({'from': kwargs['frm']})
            del kwargs['frm']
        data.update(kwargs)
        post = urllib.urlencode(data)
        #request = urllib2.Request(url, post)
        #grab implementation
        g.setup(post=data)
        try:
            self._response = g.go(url)
        except GrabError, e:
            self.http_error = {
                'code': e[0],
                'content': e[1]
            }
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

    def get_credit_info(self):
        self.forge_request(url='get_credit_info.cgi')
        #self._content = self._response.read()
        self._content = self._response.body
        return self._content

    def send_message(self, phone, message, frm=FROM, flash=0):
        frm = frm[:11] if len(frm) > 11 else frm
        if isinstance(message, unicode):
            message = message.encode('cp1251')
        else:
            message = message.decode('utf-8').encode('cp1251')
        self.forge_request(phone=phone, message=message, frm=frm)
        #if settings.DEBUG_SMS:
        #    self.forge_request(phone=SMS_GUY, message=message, frm=frm)

    def sms_status2(self, mid):
        self.forge_request(mess_id=mid, url='sms_status2.cgi')
        #self._content = self._response.read()
        self._content = self._response.body
        return self._content
