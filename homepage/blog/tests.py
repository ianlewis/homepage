#:coding=utf-8:

import mock

from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import (
    TestCase,
    RequestFactory,
)

from homepage.blog.models import Post, Tag
from homepage.blog import views

__all__ = (
    "ViewTest"
    "FeedRedirectTest",
)

class ViewTest(TestCase):
    """
    Simple test to test views
    """
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='admin', email='admin@example.com', password='top_secret')
        self.post = Post.objects.create(
            author=self.user,
            slug="test-slug",
            title="Test Title",
            content="Test Content",
            active=True,
        )
        self.post.tags.add(Tag.objects.create(
            name="tagname",
        ))

    def test_blog_detail(self):
        """
        Test the blog detail page
        """
        req = self.factory.get("/en/test-slug")
        resp = views.blog_detail(req, locale=self.post.locale, slug=self.post.slug)
        self.assertEqual(resp.status_code, 200)

    def test_blog_page(self):
        """
        Test the blog list page
        """
        req = self.factory.get("/en/")
        resp = views.blog_page(req, locale=self.post.locale)
        self.assertContains(resp, self.post.title, status_code=200)

    def test_tag_page(self):
        """
        Test the blog list page (by tag)
        """
        req = self.factory.get("/en/tagname")
        resp = views.tag_page(req, locale=self.post.locale, tag="tagname")
        self.assertContains(resp, self.post.title, status_code=200)

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
