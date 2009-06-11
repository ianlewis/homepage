# Create your views here.
from django.views.generic.list_detail import object_list,object_detail
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404

from lifestream.util.decorators import allow_methods
from models import *
from decorators import *

@staff_member_required
@allow_methods('GET')
def blog_detail_preview(request, object_id):
    object = Post.objects.get(pk=object_id)
    defaults = {
        "queryset": Post.objects.all(),
        "object_id": object_id,
        "extra_context": {"locale": object.locale},
    }
    return object_detail(request, **defaults)

@allow_methods('GET')
@feed_redirect
def blog_page(request, locale="en"):
    return object_list(request, 
        Post.objects.published().filter(locale=locale),
        extra_context={"locale":locale},
    )

@allow_methods('GET')
def blog_detail(request, slug, locale="en"):
    defaults = {
        "queryset": Post.objects.published().filter(locale=locale),
        "slug": slug,
        "extra_context": {"locale": locale},
    }
    return object_detail(request, **defaults)

@allow_methods('GET')
def tag_page(request, tag, locale="en"):
    from tagging.views import tagged_object_list
    return tagged_object_list(
        request,
        queryset_or_model=Post.objects.published().filter(locale=locale),
        tag=tag,
        template_name="blog/post_list.html",
        extra_context={'locale':locale},
    )
