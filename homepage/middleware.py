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


from django.conf import settings
from django.core.cache import cache
from django.utils.cache import get_cache_key, learn_cache_key, patch_response_headers, get_max_age

class UpdateCacheMiddleware(object):
    """
    Response-phase cache middleware that updates the cache if the response is
    cacheable.

    Must be used as part of the two-part update/fetch cache middleware.
    UpdateCacheMiddleware must be the first piece of middleware in
    MIDDLEWARE_CLASSES so that it'll get called last during the response phase.
    """
    def __init__(self):
        self.cache_timeout = settings.CACHE_MIDDLEWARE_SECONDS
        self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
        self.cache_anonymous_only = getattr(settings, 'CACHE_MIDDLEWARE_ANONYMOUS_ONLY', False)

    def process_response(self, request, response):
        """Sets the cache, if needed."""
        if not hasattr(request, '_cache_update_cache') or not request._cache_update_cache:
            # We don't need to update the cache, just return.
            logging.info("%s: _cache_update_cache is false" % request.path)
            return response
        if request.method != 'GET':
            # This is a stronger requirement than above. It is needed
            # because of interactions between this middleware and the
            # HTTPMiddleware, which throws the body of a HEAD-request
            # away before this middleware gets a chance to cache it.
            return response
        if not response.status_code == 200:
            logging.info("%s: status_code is not 200" % request.path)
            return response
        # Try to get the timeout from the "max-age" section of the "Cache-
        # Control" header before reverting to using the default cache_timeout
        # length.
        timeout = get_max_age(response)
        if timeout == None:
            timeout = self.cache_timeout
        elif timeout == 0:
            # max-age was set to 0, don't bother caching.
            logging.info("%s: max-age was set to 0, don't bother caching." % request.path)
            return response
        patch_response_headers(response, timeout)
        if timeout:
            cache_key = learn_cache_key(request, response, timeout, self.key_prefix)
            logging.info("%s: learned cache key: %s" % (request.path, cache_key))
            cache.set(cache_key, response, timeout)
            logging.info("set cache: %s,%s\n\n%s" % (cache, timeout, cache.get(cache_key)))
        return response

class FetchFromCacheMiddleware(object):
    """
    Request-phase cache middleware that fetches a page from the cache.

    Must be used as part of the two-part update/fetch cache middleware.
    FetchFromCacheMiddleware must be the last piece of middleware in
    MIDDLEWARE_CLASSES so that it'll get called last during the request phase.
    """
    def __init__(self):
        self.cache_timeout = settings.CACHE_MIDDLEWARE_SECONDS
        self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
        self.cache_anonymous_only = getattr(settings, 'CACHE_MIDDLEWARE_ANONYMOUS_ONLY', False)

    def process_request(self, request):
        """
        Checks whether the page is already cached and returns the cached
        version if available.
        """
        if self.cache_anonymous_only:
            assert hasattr(request, 'user'), "The Django cache middleware with CACHE_MIDDLEWARE_ANONYMOUS_ONLY=True requires authentication middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.auth.middleware.AuthenticationMiddleware' before the CacheMiddleware."

        if not request.method in ('GET', 'HEAD') or request.GET:
            logging.info("%s: not get or head request" % request.path)
            request._cache_update_cache = False
            return None # Don't bother checking the cache.

        if self.cache_anonymous_only and request.user.is_authenticated():
            logging.info("anonymous only")
            request._cache_update_cache = False
            return None # Don't cache requests from authenticated users.

        cache_key = get_cache_key(request, self.key_prefix)
        if cache_key is None:
            logging.info("%s: cache key is none. No cache information available, need to rebuild." % request.path)
            request._cache_update_cache = True
            return None # No cache information available, need to rebuild.

        response = cache.get(cache_key, None)
        if response is None:
            logging.info("%s: response is none. No cache information available, need to rebuild." % request.path)
            request._cache_update_cache = True
            return None # No cache information available, need to rebuild.

        request._cache_update_cache = False
        logging.info("return cached response %s:\n\n%s" % (cache,response))
        return response

class CacheMiddleware(UpdateCacheMiddleware, FetchFromCacheMiddleware):
    """
    Cache middleware that provides basic behavior for many simple sites.

    Also used as the hook point for the cache decorator, which is generated
    using the decorator-from-middleware utility.
    """
    def __init__(self, cache_timeout=None, key_prefix=None, cache_anonymous_only=None):
        self.cache_timeout = cache_timeout
        if cache_timeout is None:
            self.cache_timeout = settings.CACHE_MIDDLEWARE_SECONDS
        self.key_prefix = key_prefix
        if key_prefix is None:
            self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
        if cache_anonymous_only is None:
            self.cache_anonymous_only = getattr(settings, 'CACHE_MIDDLEWARE_ANONYMOUS_ONLY', False)
        else:
            self.cache_anonymous_only = cache_anonymous_only
