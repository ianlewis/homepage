# Create your views here.
from django.views.generic import list_detail

from models import *

def blog_page(request, locale="en", page=1):
    defaults = {
        "queryset": Post.objects.active().filter(locale=locale),
        "paginate_by": 10,
        "page": page,
    }
    return list_detail.object_list(request, **defaults)

def blog_detail(request, slug, locale="en"):
    defaults = {
        "queryset": Post.objects.active().filter(locale=locale),
        "slug": slug,
    }
    return list_detail.object_detail(request, **defaults)

