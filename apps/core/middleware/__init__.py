# coding: utf-8
from django.contrib import auth
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.views.debug import ExceptionReporter
from django.contrib.sites.models import Site
from django.template.loader import get_template
from django.template import Context
import logging
import sys
import traceback


logger = logging.getLogger(__name__)


class IE6BanMiddleware(object):
    def process_request(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', 'notie')
        user = request.user
        if 'msie 6.0' in user_agent.title().lower()\
            or 'msie 5.5' in user_agent.title().lower():
            template = get_template('get_a_working_browser.html')
            out = template.render(Context())
            response = HttpResponse()
            response.write(out)
            return response

class ExceptionMiddleware(object):
    """Logs the traceback"""
    def process_exception(self, request, exception):
        current_site = Site.objects.get_current()

        # log the traceback
        tb = traceback.format_exc()
        logger.error('Traceback from %s\n%s' % (request.get_full_path(), tb))

        # if it's a 404 don't email or return special 500 page
        type, val, trace = sys.exc_info()
        if type == Http404:
          return

        # an error besides Http404 and we mail the admins
        subject = 'TRACEBACK from %s: %s' % (current_site, request.get_full_path())

        # return the DEBUG 500 page to the client
        er = ExceptionReporter(request, *sys.exc_info())
        return HttpResponseServerError(er.get_traceback_html())