#:coding=utf-8:

import mock

from django.test import (
    TestCase,
    RequestFactory,
)

from homepage.health.middleware import HealthMiddleware

__all__ = (
    "HealthMiddlewareTest",
)

class HealthMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_healthz(self):
        """
        Tests the healthz endpoint
        """
        request = self.factory.get("/_status/healthz")
        middleware = HealthMiddleware()
        response = middleware.process_request(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "OK")

    def test_readiness(self):
        """
        Tests when the readiness endpoint is ok.
        """
        request = self.factory.get("/_status/readiness")
        middleware = HealthMiddleware()
        response = middleware.process_request(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "OK")

    def test_readiness_bad(self):
        """
        Tests when the readiness endpoint is not ok.
        """
        from django import db
        with mock.patch.object(db, 'connection') as connection:
            connection.cursor().fetchone.side_effect = Exception("No DB!")

            request = self.factory.get("/_status/readiness")
            middleware = HealthMiddleware()
            response = middleware.process_request(request)

            self.assertEqual(response.status_code, 500)
            self.assertTrue(response.content.startswith("db:"))
