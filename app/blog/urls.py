#:coding=utf8:

from django.conf.urls.defaults import *

from feeds import *

urlpatterns = patterns('django.views.generic.simple',
    # Old tag url redirect
    url(r'^(?P<locale>\w{2})/(?P<tag>[^/]+);$', 'redirect_to', {'url': '/%(locale)s/tag/%(tag)s'}, name='old_blog_tag_page'),
)

feeds = {
    'enfeed': LatestEnglishBlogEntries,
    'jpfeed': LatestJapaneseBlogEntries,
}

urlpatterns += patterns('blog.views',
    url(r'^admin/blog/post/(?P<object_id>[0-9]+)/preview$', 'blog_detail_preview', name='blog_detail_preview'),

    url(r'^(?P<locale>\w{2})/tag/(?P<tag>.+)$', 'tag_page', name='blog_tag_page'),
        
    url(r'^(?P<locale>\w{2})/(?P<slug>[^/]+)/?$', 'blog_detail', name='blog_detail'),
    url(r'^(?P<locale>\w{2})/?$', 'blog_page', name="blog_page"),
)

urlpatterns += patterns('django.contrib.syndication.views',
    url(r'^feed/(?P<url>.*)$', 'feed', {'feed_dict':feeds}, name='blog_feeds'),
)
