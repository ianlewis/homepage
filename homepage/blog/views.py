#:coding=utf8:

import time

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.shortcuts import render
from django.http import Http404
from django.conf import settings

from homepage.blog.models import Post
from homepage.blog.decorators import feed_redirect
from homepage.blog.templatetags.blog_tags import to_html
from homepage.blog.pagination import Page 
from homepage.blog.stub import blog_stub
from homepage.blog.pb import blog_pb2

@require_http_methods(['GET', 'HEAD'])
def blog_detail(request, locale, slug):
    reply = blog_stub.GetPost(
        blog_pb2.GetPostRequest(
            slug=slug,        
            locale=locale,
        )
    )

    if not reply.post.active:
        raise Http404("Post not found")

    context = {}
    context["object"] = reply.post
    context["locale"] = locale

    if locale in settings.RSS_FEED_URLS:
        context['rss_feed_url'] = settings.RSS_FEED_URLS[locale]

    context["tags"] = [tag.name for tag in reply.post.tags]

    context['content_html'] = to_html(reply.post)

    return render(request, 'blog/post_detail.html', context)

@staff_member_required
@require_http_methods(['GET', 'HEAD'])
def blog_detail_preview(request, locale, slug):
    reply = blog_stub.GetPost(
        blog_pb2.GetPostRequest(
            slug=slug,        
            locale=locale,
        )
    )

    context = {}
    context["object"] = reply.post
    context["locale"] = locale

    if locale in settings.RSS_FEED_URLS:
        context['rss_feed_url'] = settings.RSS_FEED_URLS[locale]

    context["tags"] = [tag.name for tag in reply.post.tags]

    context['content_html'] = to_html(reply.post)

    return render(request, 'blog/post_detail.html', context)

@require_http_methods(['GET', 'HEAD'])
def blog_page(request, locale):
    # Validate the page number
    try:
        page_number = int(request.GET.get("page", "1"))
    except ValueError:
        page_number = 1

    if page_number < 1:
        raise Http404("Less than 1")

    pub_date = int(time.time())

    page_future = blog_stub.GetPage.future(
        blog_pb2.GetPageRequest(
            locale=locale,
            pub_date=pub_date,
            active=blog_pb2.PUBLISHED,
            # Page number is zero indexed
            page_number=page_number - 1,
            result_per_page=10,
        )
    )

    num_pages_future = blog_stub.GetNumPages.future(
        blog_pb2.GetNumPagesRequest(
            locale=locale,
            pub_date=pub_date,
            active=blog_pb2.PUBLISHED,
            result_per_page=10,
        )
    )
    
    page_reply = page_future.result()
    num_pages_reply = num_pages_future.result()

    if page_number > num_pages_reply.num_pages:
        raise Http404("Page doesn't exist.")

    context = {}
    context["locale"] = locale
    context["is_paginated"] = num_pages_reply.num_pages > 1
    context["page_obj"] = Page(page_number, num_pages_reply.num_pages)
    context["object_list"] = page_reply.posts
    if locale in settings.RSS_FEED_URLS:
        context['rss_feed_url'] = settings.RSS_FEED_URLS[locale]

    return render(request, 'blog/post_list.html', context)


@require_http_methods(['GET', 'HEAD'])
def tag_page(request, locale, tag):
    # Validate the page number
    try:
        page_number = int(request.GET.get("page", "1"))
    except ValueError:
        page_number = 1

    if page_number < 1:
        raise Http404("Less than 1")

    pub_date = int(time.time())

    page_future = blog_stub.GetPage.future(
        blog_pb2.GetPageRequest(
            locale=locale,
            pub_date=pub_date,
            tag=blog_pb2.Tag(name=tag),
            active=blog_pb2.PUBLISHED,
            # Page number is zero indexed
            page_number=page_number - 1,
            result_per_page=10,
        )
    )

    num_pages_future = blog_stub.GetNumPages.future(
        blog_pb2.GetNumPagesRequest(
            locale=locale,
            pub_date=pub_date,
            tag=blog_pb2.Tag(name=tag),
            active=blog_pb2.PUBLISHED,
            result_per_page=10,
        )
    )
    
    page_reply = page_future.result()
    num_pages_reply = num_pages_future.result()

    if page_number > num_pages_reply.num_pages:
        raise Http404("Page doesn't exist.")

    context = {}
    context["locale"] = locale
    context["tag"] = tag
    context["is_paginated"] = num_pages_reply.num_pages > 1
    context["page_obj"] = Page(page_number, num_pages_reply.num_pages)
    context["object_list"] = page_reply.posts
    if locale in settings.RSS_FEED_URLS:
        context['rss_feed_url'] = settings.RSS_FEED_URLS[locale]

    return render(request, 'blog/post_list.html', context)
