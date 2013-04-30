# Create your views here.
# coding: utf-8
from apps.core.helpers import render_to
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

@render_to('index.html')
def index(request):
    return {}

@render_to('500.html')
def test_500(request):
    if settings.TEST_500_ENABLE:
        raise ImproperlyConfigured("test 500")
    return {}
