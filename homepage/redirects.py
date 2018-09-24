#:coding=utf8:

from django.conf.urls import url
from django.utils.http import urlquote
from django.http import (
    HttpResponseRedirect,
    HttpResponsePermanentRedirect,
    HttpResponseGone,
)


def redirect_to(request, url, permanent=True, **kwargs):
    """
    A copy of the redirect_to view from django.views.generic.simple
    Copied since redirect_to doesn't work for urls that contain non-ascii
    keyword arguments.
    """
    if url is not None:
        klass = (permanent and HttpResponsePermanentRedirect
                 or HttpResponseRedirect)
        quoted_kwargs = {}
        for k, v in kwargs.iteritems():
            quoted_kwargs[k] = urlquote(v)
        return klass(url % quoted_kwargs)
    else:
        return HttpResponseGone()

urlpatterns = [
    url(r'^projects(?:/.*)?$', redirect_to, {'url': '/'}, name="projects_redirect"),

    #url(r'^en/about(?:/.*)?$', redirect_to, {'url': '/'}, name="en_about_redirect"),
    url(r'^jp/about(?:/.*)?$', redirect_to, {'url': '/en/about/'}, name="jp_about_redirect"),
    url(r'^jp/aboutjp$', redirect_to, {'url': '/en/about/'}, name="jp_about_redirect2"),

    # Really old legacy urls from the b2evo blog
    url(r'^index.php/(?P<locale>\w{2})/?$', redirect_to, {'url': '/%(locale)s/'}),
    url(r'^index.php$', redirect_to, {'url': '/en/'}),
    url(r'^index.php/(?P<locale>\w{2})/(?P<slug>[^/]+)/?$', redirect_to, {'url': '/%(locale)s/%(slug)s'}),

    url(r'^en/(?P<tag_name>.+)\;', redirect_to, {'url': '/en/tag/%(tag_name)s'}),
    url(r'^jp/(?P<tag_name>.+)\;', redirect_to, {'url': '/jp/tag/%(tag_name)s'}),

    # Old lifestream urls.
    url(r'^items/', redirect_to, {'url': '/'}),
    url(r'^page/(?P<page>\d+)/?$', redirect_to, {'url': '/'}, name="lifestream_page_redirect"),
]
