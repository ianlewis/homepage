#:coding=utf8:

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
