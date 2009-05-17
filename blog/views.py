# Create your views here.
from django.views.generic.list_detail import object_list,object_detail

from models import *

def blog_page(request, locale="en"):
    defaults = {
        "queryset": Post.objects.active().filter(locale=locale),
    }
    return object_list(request, **defaults)

def blog_detail(request, slug, locale="en"):
    defaults = {
        "queryset": Post.objects.active().filter(locale=locale),
        "slug": slug,
    }
    return object_detail(request, **defaults)

