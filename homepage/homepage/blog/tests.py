#:coding=utf-8:

import mock

from django.conf import settings
from django.test import (
    TestCase,
    RequestFactory,
)

__all__ = (
    "FeedRedirectTest",
)

class FeedRedirectTest(TestCase):
    """
    Test's that feed urls without a trailing slash
    are ridirected to their proper url.
    """

    def test_en_feed_redirect(self):
        resp = self.client.get("/feed/enfeed", follow=False)
        # Redirects permanently
        self.assertRedirects(resp, settings.RSS_FEED_URLS["en"],
                status_code=301, fetch_redirect_response=False)
            
    def test_jp_feed_redirect(self):
        resp = self.client.get("/feed/jpfeed", follow=False)
        # Redirects permanently
        self.assertRedirects(resp, settings.RSS_FEED_URLS["jp"],
                status_code=301, fetch_redirect_response=False)
