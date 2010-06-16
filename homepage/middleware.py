#:coding=utf8:

import re

#from django.http import HttpResponseRedirect
#from django.contrib.sites.models import Site
#from django.conf import settings

#class WWWRedirectMiddleware(object):
#    def process_request(self, request):
#        current_site = Site.objects.get_current()
#        if not settings.DEBUG and \
#           request.META['HTTP_HOST'] != current_site.domain:
#            return HttpResponseRedirect('http://%s%s' % (current_site.domain, request.path))

from jogging import logging

class GoogleAnalyticsStripCookieMiddleware(object):
    strip_re = re.compile(r'(__utm.=.+?(?:; |$))')
    def process_request(self, request):
        try:
            before = request.META['HTTP_COOKIE']
            cookie = self.strip_re.sub('', request.META['HTTP_COOKIE'])
            request.META['HTTP_COOKIE'] = cookie
            logging.info("Stripped cookies for: %s\n\nBefore:\n%s\n\nAfter:\n%s" % (request.path, before, request.META['HTTP_COOKIE']))
        except Exception, e:
            logging.exception("Could not script analytics cookies", e, request)
