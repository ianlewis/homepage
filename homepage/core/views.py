#:coding=utf8:

import time

from django.http import HttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.contrib.staticfiles.views import serve
from django.conf import settings

from django.shortcuts import render

from constance import config

import homepage
from homepage.blog.stub import blog_stub
from homepage.blog.pb import blog_pb2


@require_http_methods(['GET', 'HEAD'])
def main_page(request):
    """
    The top page.
    Shows a few English and Japanese blog posts as a teaser.
    """
    pub_date = int(time.time())

    en_page_future = blog_stub.GetPage.future(
        blog_pb2.GetPageRequest(
            locale="en",
            pub_date=pub_date,
            active=blog_pb2.PUBLISHED,
            # Page number is zero indexed
            page_number=0,
            result_per_page=10,
        )
    )
    jp_page_future = blog_stub.GetPage.future(
        blog_pb2.GetPageRequest(
            locale="jp",
            pub_date=pub_date,
            active=blog_pb2.PUBLISHED,
            # Page number is zero indexed
            page_number=0,
            result_per_page=5,
        )
    )

    en_reply = en_page_future.result()
    jp_reply = jp_page_future.result()

    return render(request, "index.html", {
        "en_rss_feed_url": settings.RSS_FEED_URLS["en"],
        "jp_rss_feed_url": settings.RSS_FEED_URLS["jp"],
        "jp_posts": jp_reply.posts,
        "en_posts": en_reply.posts,
    })


@require_http_methods(['GET', 'HEAD'])
@cache_page(60 * 15)
def robots(request):
    """
    The robots.txt configuration.
    This robots.txt is taken from the constance config set in the admin.

    See: https://en.wikipedia.org/wiki/Robots_exclusion_standard
    """
    return HttpResponse(config.robots_txt, content_type='text/plain')

@require_http_methods(['GET', 'HEAD'])
@cache_page(60 * 15)
def security_txt(request):
    """
    security.txt for security issue disclosure.
    See: https://securitytxt.org/
    """
    if len(config.security_txt) == 0:
        raise Http404("Not found")
    return HttpResponse(config.security_txt, content_type='text/plain')

@require_http_methods(['GET', 'HEAD'])
@cache_page(60 * 15)
def security_txt_sig(request):
    """
    Signature for security.txt
    """
    if len(config.security_txt_sig) == 0:
        raise Http404("Not found")
    return HttpResponse(config.security_txt_sig, content_type='text/plain')

@require_http_methods(['GET', 'HEAD'])
@cache_page(60 * 15)
def favicon(request):
    """
    Returns the favicon
    """
    # We specify the path here so insecure should be ok.
    return serve(request, 'extra/favicon.ico', insecure=True)

@require_http_methods(['GET', 'HEAD'])
@cache_page(60 * 15)
def version(request):
    return HttpResponse(homepage.__version__, content_type='text/plain')
