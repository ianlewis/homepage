#:coding=utf8:

from django.http import HttpResponseRedirect 
#from django.views.generic.list_detail import object_list, object_detail
from django.views.decorators.http import require_http_methods
from django.shortcuts import render

from homepage.blog.models import Post

@require_http_methods(['GET', 'HEAD'])
def main_page(request):
    en_posts = Post.objects.published().filter(locale="en").order_by("-pub_date")
    jp_posts = Post.objects.published().filter(locale="jp").order_by("-pub_date")
    
    return render(request, "index.html", {
        #'latest_tweet': latest_tweet,
        "jp_posts": jp_posts,
        "en_posts": en_posts,
    })
