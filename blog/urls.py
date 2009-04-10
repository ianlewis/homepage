#:coding=utf8:

from django.conf.urls.defaults import *

urlpatterns = patterns('blog.views',
    url(r'^(?P<locale>\w{2})/?$', 'blog_page', name="blog_page"),
    url(r'^(?P<locale>\w{2})/page/(?P<page>\d)/?', 'blog_page', name='blog_page_paged'),
    url(r'^(?P<locale>\w{2})/[^/]+/?', 'blog_detail', name='blog_detail'),
)
