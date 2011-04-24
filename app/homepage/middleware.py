#:coding=utf8:

import re

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
