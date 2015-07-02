#:coding=utf8:

import re

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseBadRequest


class HostRedirectMiddleware(object):
    """
    Host middleware that redirects from a naked domain
    to the www subdomain.
    """
    def process_request(self, request):
        if not settings.DEBUG and not request.get_host().startswith("www."):
            if request.method == 'GET':
                return HttpResponseRedirect("%s://www.%s%s" % (
                    request.is_secure() and 'https' or 'http',
                    request.get_host(),
                    request.get_full_path(),
                ))
            else:
                return HttpResponseBadRequest("Bad Domain")


class GoogleAnalyticsStripCookieMiddleware(object):
    strip_re = re.compile(r'(__utm.=.+?(?:; |$))')

    def process_request(self, request):
        try:
            before = request.META.get('HTTP_COOKIE')
            if before:
                cookie = self.strip_re.sub('', request.META['HTTP_COOKIE'])
                request.META['HTTP_COOKIE'] = cookie
        except Exception, e:
            from jogging import logging
            logging.exception("Could not script analytics cookies", e, request)
