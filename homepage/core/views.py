#:coding=utf8:

from django.http import HttpResponseRedirect 
#from django.views.generic.list_detail import object_list, object_detail
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.db.models import Q

from tagging.views import tagged_object_list
from lifestream.models import Item

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

#@require_http_methods(['GET', 'HEAD'])
#def tag_page(request, tag):
#    return tagged_object_list(
#        request,
#        queryset_or_model=Item.objects.published(),
#        tag=tag,
#        extra_context={
#            "rss_feed_url": reverse("lifestream_tag_feeds", kwargs={"tag": tag}),
#        }
#    )

#@require_http_methods(['GET', 'HEAD'])
#def search(request):
#    # Get unique keywords
#    raw_keywords = request.GET.get("q") or ""
#    domain = request.GET.get("domain")
#    keywords = list(set((raw_keywords).split()))
#    if keywords: 
#        queryset = Item.objects.published()
#        for keyword in keywords:
#            queryset = queryset.filter(Q(title__icontains=keyword) | Q(clean_content__icontains=keyword))
#        if domain:
#            queryset = queryset.filter(feed__domain=domain)
#    else:
#        #queryset = Item.objects.none()
#        return HttpResponseRedirect(reverse('main_page'))
#
#    return object_list(
#        request,
#        template_name='lifestream/item_search.html',
#        queryset=queryset,
#        extra_context={
#            'keywords': raw_keywords,
#        },
#    )
