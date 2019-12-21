# :coding=utf-8:

import logging

from django.http import HttpResponse, HttpResponseServerError

logger = logging.getLogger("homepage.health.middleware")


class HealthCheckMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        # One-time configuration and initialization.

    def process_request(self, request):
        if request.method == "GET":
            if request.path == "/_status/readiness":
                return self.readiness(request)
            elif request.path == "/_status/healthz":
                return self.healthz(request)

    def __call__(self, request):
        if self.get_response:
            self.process_request(request)
            return self.get_response(request)
        else:
            raise RuntimeError(
                "No get_response callable given. Callable middleware not supported."
            )

    def healthz(self, request):
        """
        Returns that the server is alive.
        """
        return HttpResponse("OK")

    def readiness(self, request):
        # Connect to each database and do a generic standard SQL query
        # that doesn't write any data and doesn't depend on any tables
        # being present.
        try:
            from django.db import connections

            for name in connections:
                cursor = connections[name].cursor()
                cursor.execute("SELECT 1;")
                row = cursor.fetchone()
                if row is None:
                    return HttpResponseServerError("db: invalid response")
        except Exception, e:
            logger.exception(e)
            return HttpResponseServerError("db: cannot connect to database.")

        # Call get_stats() to connect to each memcached instance and get it's stats.
        # This can effectively check if each is online.
        try:
            from django.core.cache import caches
            from django.core.cache.backends.memcached import BaseMemcachedCache

            for cache in caches.all():
                if isinstance(cache, BaseMemcachedCache):
                    stats = cache._cache.get_stats()
                    if len(stats) != len(cache._servers):
                        return HttpResponseServerError(
                            "cache: cannot connect to cache."
                        )
        except Exception, e:
            logger.exception(e)
            return HttpResponseServerError("cache: cannot connect to cache.")

        return HttpResponse("OK")
