#:coding=utf8:

import re

from django.http import HttpResponseRedirect
from django.contrib.sites.models import Site
from django.conf import settings

class WWWRedirectMiddleware(object):
    def process_request(self, request):
        current_site = Site.objects.get_current()
        if not settings.DEBUG and \
           request.META['HTTP_HOST'] != current_site.domain:
            return HttpResponseRedirect('http://%s%s' % (current_site.domain, request.path))

class GoogleAnalyticsStripCookieMiddleware(object):
    strip_re = re.compile(r'(__utm.=.+?(?:; |$))')
    def process_request(self, request):
        try:
            cookie = self.strip_re.sub('', request.META['HTTP_COOKIE'])
            request.META['HTTP_COOKIE'] = cookie
        except: pass
