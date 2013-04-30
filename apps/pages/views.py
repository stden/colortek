# Create your views here.
from apps.core.shortcuts import direct_to_template
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect

from apps.pages.models import Page

def page(request, url):
    template = 'pages/page.html'
    pages = Page.objects.filter(url__iexact="/%s" % url)
    page = pages[0] if pages else None
    if not page:
        if url[-1] != '/':
            return redirect(url + '/')
        else:
            raise Http404("No such url found")
    template = page.template or template
    return direct_to_template(request, template, {'page': page})
