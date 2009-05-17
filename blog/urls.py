#:coding=utf8:

from django.conf.urls.defaults import *

urlpatterns = patterns('django.views.generic.simple',
    # Old tag url redirect
    url(r'^(?P<locale>\w{2})/(?P<tag>[^/]+);$', 'redirect_to', {'url': '/%(locale)s/tag/%(tag)s'}, name='old_blog_tag_page'),
)

urlpatterns += patterns('blog.views',
    url(r'^(?P<locale>\w{2})/tag/(?P<tag>.+)$', 'tag_page', name='blog_tag_page'),
        
    url(r'^(?P<locale>\w{2})/(?P<slug>[^/]+)/?$', 'blog_detail', name='blog_detail'),
    url(r'^(?P<locale>\w{2})/?$', 'blog_page', name="blog_page"),
)
