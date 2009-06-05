#:coding=utf8:

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^page/(?P<page>\d+)/?$', 'django.views.generic.simple.redirect_to', {'url': '/?page=%(page)s'}, name="lifestream_page_redirect"),
    url(r'^projects(?:/.*)?$', 'django.views.generic.simple.redirect_to', {'url': '/'}, name="projects_redirect"),
    url(r'^en/about(?:/.*)?$', 'django.views.generic.simple.redirect_to', {'url': '/'}, name="en_about_redirect"),
    url(r'^jp/about(?:/.*)?$', 'django.views.generic.simple.redirect_to', {'url': '/'}, name="jp_about_redirect"),
)
