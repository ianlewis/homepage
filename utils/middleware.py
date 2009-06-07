#:coding=utf8:

from django.http import HttpResponseRedirect
from django.contrib.sites.models import Site
from django.conf import settings

class WWWRedirectMiddleware(object):
    def process_request(self, request):
        if not settings.DEBUG and not request.META['HTTP_HOST'].startswith('www.'):
            current_site = Site.objects.get_current()
            return HttpResponseRedirect('http://%s%s' % (current_site.domain, request.path))
