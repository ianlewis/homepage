#:coding=utf8:

from django.conf.urls import url
from django.views.generic import RedirectView
from django.conf import settings

from homepage.blog.feeds import (
    LatestEnglishBlogEntries,
    LatestJapaneseBlogEntries,
)

from homepage.redirects import redirect_to
from homepage.blog import views

urlpatterns = [
    # Old tag url redirect
    url(r'^(?P<locale>jp|en)/(?P<tag>[^/]+);$', redirect_to,
        {'url': '/%(locale)s/tag/%(tag)s'}, name='old_blog_tag_page'),
]

urlpatterns += [
    url(r'^admin/blog/post/(?P<pk>[0-9]+)/preview$',
        views.blog_detail_preview, name='blog_detail_preview'),

    url(r'^(?P<locale>jp|en)/tag/(?P<tag>.+)$',
        views.tag_page, name='blog_tag_page'),

    url(r'^(?P<locale>jp|en)/(?P<slug>[^/]+)/?$',
        views.blog_detail, name='blog_detail'),
    url(r'^(?P<locale>jp|en)/?$', views.blog_page, name="blog_page"),
]

# feed urls
urlpatterns += [
    url(r'^feed/enfeed/?$', RedirectView.as_view(url=settings.RSS_FEED_URLS["en"], permanent=True)),
    url(r'^feed/enfeed/(?P<tag>.+)$', RedirectView.as_view(url=settings.RSS_FEED_URLS["en"], permanent=True)),
    url(r'^_secret/feed/enfeed/$', LatestEnglishBlogEntries(), name='blog_feed_en'),

    url(r'^feed/jpfeed/?$', RedirectView.as_view(url=settings.RSS_FEED_URLS["jp"], permanent=True)),
    url(r'^feed/jpfeed/(?P<tag>.+)$', RedirectView.as_view(url=settings.RSS_FEED_URLS["jp"], permanent=True)),
    url(r'^_secret/feed/jpfeed/$', LatestJapaneseBlogEntries(), name='blog_feed_jp'),
]
