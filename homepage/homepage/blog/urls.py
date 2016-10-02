#:coding=utf8:

from django.conf.urls import patterns, url
from django.views.generic import RedirectView

from homepage.blog.feeds import (
    LatestEnglishBlogEntries,
    LatestJapaneseBlogEntries,
)

from homepage.redirects import redirect_to

urlpatterns = patterns(
    'django.views.generic.simple',

    # Old tag url redirect
    url(r'^(?P<locale>jp|en)/(?P<tag>[^/]+);$', redirect_to,
        {'url': '/%(locale)s/tag/%(tag)s'}, name='old_blog_tag_page'),
)

urlpatterns += patterns(
    'homepage.blog.views',

    url(r'^admin/blog/post/(?P<pk>[0-9]+)/preview$',
        'blog_detail_preview', name='blog_detail_preview'),

    url(r'^(?P<locale>jp|en)/tag/(?P<tag>.+)$',
        'tag_page', name='blog_tag_page'),

    url(r'^(?P<locale>jp|en)/(?P<slug>[^/]+)/?$',
        'blog_detail', name='blog_detail'),
    url(r'^(?P<locale>jp|en)/?$', 'blog_page', name="blog_page"),
)

urlpatterns += patterns(
    '',
    url(r'^feed/enfeed$', RedirectView.as_view(url='/feed/enfeed/')),
    url(r'^feed/enfeed/$', LatestEnglishBlogEntries(), name='blog_feed_en'),
    url(r'^feed/enfeed/(?P<tag>.+)$', LatestEnglishBlogEntries(),
        name='blog_feed_en_tag'),

    url(r'^feed/jpfeed$', RedirectView.as_view(url='/feed/jpfeed/')),
    url(r'^feed/jpfeed/$', LatestJapaneseBlogEntries(), name='blog_feed_jp'),
    url(r'^feed/jpfeed/(?P<tag>.+)$', LatestJapaneseBlogEntries(),
        name='blog_feed_jp_tag'),
)
