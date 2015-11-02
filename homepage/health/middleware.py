#:coding=utf8:

from django.http import HttpResponse, HttpResponseServerError

import homepage


class HealthMiddleware(object):
    """
    Health middleware that returns the results of a health check.

    Should be placed as the first middleware in MIDDLEWARE_CLASSES.
    """

    def process_request(self, request):
        if request.method == "GET":
            if request.path == "/_status/healthz":
                return self.healthz(request)
            elif request.path == "/_status/version":
                return self.version(request)

    def healthz(self, request):
        try:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT 1;")
            row = cursor.fetchone()
            if row is None:
                return HttpResponseServerError("db: invalid response")
        except Exception:
            return HttpResponseServerError("db: cannot connect to database.")
        return HttpResponse("OK")

    def version(self, request):
        return HttpResponse(homepage.__version__)
