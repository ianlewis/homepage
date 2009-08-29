#:coding=utf8:

from django.conf.urls.defaults import *

urlpatterns = patterns('django.views.generic.simple',
    url(r'^page/(?P<page>\d+)/?$', 'redirect_to', {'url': '/?page=%(page)s'}, name="lifestream_page_redirect"),
    url(r'^projects(?:/.*)?$', 'redirect_to', {'url': '/'}, name="projects_redirect"),
    url(r'^en/about(?:/.*)?$', 'redirect_to', {'url': '/'}, name="en_about_redirect"),
    url(r'^jp/about(?:/.*)?$', 'redirect_to', {'url': '/'}, name="jp_about_redirect"),

    url(r'^feed/?$', 'redirect_to', {'url': '/feeds/recent'}),

    # Legacy urls for the blog
    url(r'^index.php/(?P<locale>\w{2})/?$', 'redirect_to', {'url': '/%(locale)s/' }),
    url(r'^index.php$', 'redirect_to', {'url': '/en/'}),
    url(r'^index.php/(?P<locale>\w{2})/(?P<slug>[^/]+)/?$', 'redirect_to', {'url': '/%(locale)s/%(slug)s'}),

    url(r'^en/(?P<tag_name>.+)\;', 'redirect_to', {'url': '/en/tag/%(tag_name)s'}),
    url(r'^jp/(?P<tag_name>.+)\;', 'redirect_to', {'url': '/jp/tag/%(tag_name)s'}),
)
