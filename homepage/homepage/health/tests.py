#:coding=utf-8:

import mock

from django.test import (
    TestCase,
    RequestFactory,
)

from homepage.health.middleware import HealthCheckMiddleware

__all__ = (
    "HealthCheckMiddlewareTest",
)

class HealthCheckMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_healthz(self):
        """
        Tests the healthz endpoint
        """
        request = self.factory.get("/_status/healthz")
        middleware = HealthCheckMiddleware()
        response = middleware.process_request(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "OK")

    def test_readiness(self):
        """
        Tests when the readiness endpoint is ok.
        """
        request = self.factory.get("/_status/readiness")
        middleware = HealthCheckMiddleware()
        response = middleware.process_request(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "OK")

    def test_readiness_bad(self):
        """
        Tests when the readiness endpoint is not ok.
        """
        from django import db
        with mock.patch.object(db, 'connections') as connections:
            # Make the connections mock iterable.
            connections.__iter__ = mock.Mock(return_value = iter(["default"]))
            connections["default"].cursor().fetchone.side_effect = Exception("No DB!")

            request = self.factory.get("/_status/readiness")
            middleware = HealthCheckMiddleware()
            response = middleware.process_request(request)

            self.assertEqual(response.status_code, 500)
            self.assertTrue(response.content.startswith("db:"))
