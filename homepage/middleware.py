#:coding=utf8:

from django.http import HttpResponseRedirect
from django.contrib.sites.models import Site
from django.conf import settings

class WWWRedirectMiddleware(object):
    def process_request(self, request):
        current_site = Site.objects.get_current()
        if not settings.DEBUG and \
           request.META['HTTP_HOST'] != current_site.domain:
            return HttpResponseRedirect('http://%s%s' % (current_site.domain, request.path))
