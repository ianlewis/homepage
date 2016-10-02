#:coding=utf-8:

import mock

from django.test import (
    TestCase,
    RequestFactory,
)

from homepage.health.middleware import HealthMiddleware

__all__ = (
    "FeedRedirectTest",
)

class FeedRedirectTest(TestCase):
    """
    Test's that feed urls without a trailing slash
    are ridirected to their proper url.
    """

    def test_en_feed_redirect(self):
        resp = self.client.get("/feed/enfeed")
        # Redirects permanently
        self.assertRedirects(resp, "/feed/enfeed/", status_code=301)
            
    def test_jp_feed_redirect(self):
        resp = self.client.get("/feed/jpfeed")
        # Redirects permanently
        self.assertRedirects(resp, "/feed/jpfeed/", status_code=301)
