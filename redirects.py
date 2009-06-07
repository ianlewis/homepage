#:coding=utf8:

from django.conf.urls.defaults import *

urlpatterns = patterns('django.views.generic.simple',
    url(r'^page/(?P<page>\d+)/?$', 'redirect_to', {'url': '/?page=%(page)s'}, name="lifestream_page_redirect"),
    url(r'^projects(?:/.*)?$', 'redirect_to', {'url': '/'}, name="projects_redirect"),
    url(r'^en/about(?:/.*)?$', 'redirect_to', {'url': '/'}, name="en_about_redirect"),
    url(r'^jp/about(?:/.*)?$', 'redirect_to', {'url': '/'}, name="jp_about_redirect"),

    url(r'^feed/?$', 'redirect_to', {'url': '/feeds/recent'}),
)
