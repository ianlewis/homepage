#:coding=utf8:

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.contrib.staticfiles.views import serve

from django.shortcuts import render

from constance import config

from homepage.blog.models import Post


@require_http_methods(['GET', 'HEAD'])
def main_page(request):
    """
    The top page.
    Shows a few English and Japanese blog posts as a teaser.
    """
    en_posts = (
        Post.objects.published().filter(locale="en").order_by("-pub_date"))
    jp_posts = (
        Post.objects.published().filter(locale="jp").order_by("-pub_date"))

    return render(request, "index.html", {
        "jp_posts": jp_posts,
        "en_posts": en_posts,
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
def favicon(request):
    return serve(request, 'extra/favicon.ico')
