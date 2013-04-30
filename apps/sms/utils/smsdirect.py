from grab import Grab, GrabError
import urllib
import urllib2
from urllib2 import URLError
from copy import deepcopy
from django.conf import settings

FROM = settings.SMS_FROM #settings.SMS_DIRECT_FROM
AUTH_DATA = {
    'login': settings.SMS_DIRECT_USER,
    'pass': settings.SMS_DIRECT_PASSWORD
}
#URL_HEADER = 'https://smsdirect.ru'

def make_db_entry(*args):
    """ givin args in the followin order: phone, name, secondname, lastname, city, date, sex"""
    return ";".join(args)


class SMSDirectParams(Exception):
    pass


class SMSDirect(object):
    def __init__(self, login='', password=''):
        self.g = Grab()
        self.auth_data = {
            'login': login if login else AUTH_DATA['login'],
            'pass': password if password else AUTH_DATA['pass']}
        self.db_info = {}
        self.dispatch_cache = {}
        self.stats_dispatch_cache = {}
        self.status = ''
        self.user_info = {
            '0': None,
            '1': None,
            '2': None,
            '3': None,
        }

    def _forge_request(self, url_pattern, **kwargs):
        url = "%s/%s" % (settings.SMS_DIRECT_URL, url_pattern)
        data = deepcopy(self.auth_data)
        data.update(**kwargs)
        post = urllib.urlencode(data)
        request = urllib2.Request(url, post)
        try:
            self.g.setup(post=data)
            response = self.g.go(url)
            if hasattr(self, 'http_error'):
                delattr(self, 'http_error')
            self.response = response
            return response
        except GrabError, e:
            self.http_error = {
                'status': True,
                'code': e[0],
                'content': e[1],
            }
        #try:
        #    response = urllib2.urlopen(request)
        #    #cleanse last http error message and content
        #    http_error = self.http_error['status'] \
        #        if hasattr(self, 'http_error') else False
        #    if http_error:
        #        del self.http_error
        #    self._response = response
        #    return response
        #except URLError, e:
        #    self.http_error = {
        #        'status': True,
        #        'code': getattr(e, 'code') if hasattr(e, 'code') else '404',
        #        'content': e.read()
        #    }
        del data
        return None

    def get_db_list(self, reload=False):
        if not hasattr(self, 'db') or reload:
            response = self._forge_request('get_db')
            self.db = response.read() if hasattr(response, 'read') else None
        return self.db

    def get_status_message(self, mid, reload=False):
        if not hasattr(self, 'status_message') or reload:
            kw = {'mid': mid}
            response = self._forge_request('status_message', **kw)
            self.status_message = response.body if response else None
            #response.read() if hasattr(response, 'read') else None
        return self.status_message

    def submit_message(self, message, to, reload=False):
        if not hasattr(self, 'message') or reload:
            kw = {'text': message.encode('utf-8'),
                'from': FROM,
                'to': to}
            response = self._forge_request('submit_message', **kw)
            #self.message = response.read() if hasattr(response, 'read') else None
        if hasattr(self, 'http_error'):
            self.message = 'not sent, error appears'
        else:
            self.status = 'possibly sent'
            self.message = response.body
        return self.message

    def submit_db(self, dbentry, create_db=False, db_name=None, role=None, id=None, reload=False):
        if isinstance(dbentry, list):
            dbentry = make_db_entry(*dbentry)
        if not hasattr(self, 'dbentry') or reload:
            kw = {'qfile': dbentry}
            if role:
                kw.update({'role': role})
            if not create_db:
                if id:
                    kw.update({'id': id})
                else:
                    raise SMSDirectParams, """With create db you should use db_name param"""
            response = self._forge_request('submit_db', **kw)
            self.dbentry = response.read() if hasattr(response, 'read') else None
        return self.dbentry

    def delete_db_entry(self, db_id, phone, reload=False):
        if not hasattr('self', 'last_deleted') or reload:
            kw = {'id': db_id, 'msisdn': phone}
            response = self._forge_request('edit_db', **kw)
            self.last_deleted = response.read() if hasattr(response, 'read') else None
        return self.last_deleted

    def get_db_status(self, db_id, reload=False):
        if not db_id in self.db_info or reload:
            kw = {'id': db_id}
            response = self._forge_request('status_db', **kw)
            self.db_info[db_id] = response.read() if hasattr(response, 'read') else None
        return self.db_info[db_id]

    def delete_db(self, db_id, reload=True):
        kw = {'id': db_id}
        db_info = self.db_info[db_id] if db_id in self.db_info else 0
        if not db_info or reload:
            response = self._forge_request('delete_db', **kw)
            content = response.read() if hasattr(response, 'read') else None
            if content == '0': #deleted
                self.db_info[db_id] = 0
        return content

    def submit_dispatch(self, typelist, db_id, message, phones=None,
        startdate=None, enddate=None, pattern=1, isurl=0,
        wappushheader=None, max_mess=100, max_mess_per_hour=20,
        day='sday0', hour='shour10', byabonentdate=0,
        number=None, localtime=1, _from=None):
        """ startdate, enddate takes HH:MM dd.mm.yy format,
        typelist 0 - database, 1 - phone list
        message - text message
        phones - msisdns users comma separated
        db_id - database id
        max_mess - max messages per day
        maxx_mess_per_hour - the same but for the hour
        pattern - use patterns (hello %USERNAME%)
        localtime - use user localtime
        """
        kw = {'typelist': typelist, 'list': db_id, 'msisdn': phones,
            'pattern': pattern, 'isurl': isurl, day: '1', hour: '1',
            'localtime': localtime, 'max_mess': max_mess,
            'max_mess_per_hour': max_mess_per_hour, 'mess': message,
            'byabonentdate': byabonentdate}
        if int(typelist) == 1 and not phones:
            raise SMSDirectParams, "You should use msisd numbers comma separated"""
        if phones: kw.update({'msisdn': phones})
        if _from: kw.update({'from': _from})
        if number: kw.update({'number': number})
        if startdate: kw.update({'startdate': startdate})
        if enddate: kw.update({'enddate': enddate})
        if wappushheader: kw.update({'wappushheader': wappushheader})
        response = self._forge_request('submit_dispatch', **kw)
        dispatch_id = response.read()
        self.dispatch_cache[dispatch_id] = {
            'status': 'initiated', 'id': 'dispatch_id',
            'type': 'db' if int(typelist) == 0 else 'phones',
            'isurl': isurl,
            }
        return dispatch_id

    def status_dispatch(self, id, reload=False):
        if not id in self.dispatch_cache or reload:
            kw = {'id': id}
            response = self._forge_request('status_dispatch', **kw)
            answer = response.read()
            status = {}
            if answer == '400':
                status.update({'status': 'approved, initiated, queued',
                    'code': answer})
            elif answer == '500':
                status.update({'status': 'inprogress, delivering',
                    'code': answer})
            elif answer == '600':
                status.update({'status': 'finishing', 'code': answer})
            elif answer == '1000':
                status.update({'status': 'cancelled, cancellation'})
            elif answer == '800':
                status.update({'status': 'successed', 'code': answer})
            elif answer == '1':
                status.update({'status': 'editable', 'code': answer})
            elif answer == '700':
                status.update({'status': 'stopped', 'code': answer})
            elif answer == '200':
                status.update({'status': 'declined (not enought funds)', 'code': answer})
            elif answer == '300':
                status.update({'status': 'declined (by moderator)', 'code': answer})
            elif answer == '1100':
                status.update({'status': 'stopped', 'code': answer})
            else:
                status.update({'status': 'unkown', 'code': answer})
            #
            if id in self.dispatch_cache:
                self.dispatch_cache[id].update(status)
            else:
                self.dispatch_cache[id] = status
        return self.dispatch_cache[id]['status']

    def stats_dispatch(self, id):
        kw = {'id': id}
        response = self._forge_request('stats_dispatch', **kw)
        answer = response.read()
        if id in self.stats_dispatch_cache:
            self.stats_dispatch_cache[id].update(answer)
        else:
            self.stats_dispatch_cache[id] = answer
        return answer

    def get_user_info(self, mode='0', reload=True):
        if isinstance(mode, int):
               mode = str(mode)
        if not self.user_info[mode] or reload:
            try:
                mode = int(mode)
            except ValueError:
                raise SMSDirectParams, "Wrong mode passed"
            kw = {'mode': mode}
            response = self._forge_request('get_user_info', **kw)
            content = response.read()
            self.user_info[str(mode)] = content
        return self.user_info[str(mode)]

if __name__ in '__main__':
    sms = SMSDirect()
    sms.get_user_info()
    print sms.user_info
