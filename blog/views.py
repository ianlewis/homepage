# Create your views here.
from django.views.generic.list_detail import object_list,object_detail
from django.http import Http404

from lifestream.util.decorators import allow_methods
from models import *

@allow_methods('GET')
def blog_page(request, locale="en"):
    return object_list(request, Post.objects.published().filter(locale=locale))

@allow_methods('GET')
def blog_detail(request, slug, locale="en"):
    defaults = {
        "queryset": Post.objects.published().filter(locale=locale),
        "slug": slug,
    }
    return object_detail(request, **defaults)

@allow_methods('GET')
def tag_page(request, tag, locale="en"):
    from tagging.utils import get_tag
    from tagging.models import TaggedItem
    #import pdb;pdb.set_trace()
    tag_instance = get_tag(tag)
    if not tag_instance:
        raise Http404

    queryset = TaggedItem.objects.get_by_model(Post.objects.published(), tag_instance)

    return object_list(request, queryset)
