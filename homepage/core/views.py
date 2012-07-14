#:coding=utf8:

from django.http import HttpResponseRedirect 
from django.views.generic.list_detail import object_list,object_detail
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.db.models import Q

from tagging.views import tagged_object_list
from lifestream.models import Item

from homepage.blog.models import Post

@require_http_methods(['GET', 'HEAD'])
def main_page(request):
    # Get latest English and Japanese post.
    try:
        en_post = Post.objects.published().filter(locale="en").latest("pub_date")
    except Post.DoesNotExist:
        en_post = None
    try:
        jp_post = Post.objects.published().filter(locale="jp").latest("pub_date")
    except Post.DoesNotExist:
        jp_post = None
    
    try:
        latest_tweet = Item.objects.published()\
                           .filter(feed__domain="twitter.com")\
                           .latest('date')
    except Item.DoesNotExist:
        latest_tweet = None
  
    return object_list(request, 
        queryset = Item.objects.published().exclude(feed__domain="twitter.com"), 
        template_name = "lifestream/main.html",
        extra_context = {
            'latest_tweet': latest_tweet,
            "jp_post": jp_post,
            "en_post": en_post,
            'rss_feed_url': reverse('lifestream_recent_feed'),
        }
    )

@require_http_methods(['GET', 'HEAD'])
def domain_page(request, domain):
    return object_list(
        request,
        queryset=Item.objects.published().filter(feed__domain=domain),
    )

@require_http_methods(['GET', 'HEAD', 'POST'])
def item_page(request, item_id):
    return object_detail(
        request,
        queryset=Item.objects.published(),
        object_id=item_id,    
    )

@require_http_methods(['GET', 'HEAD'])
def tag_page(request, tag):
    return tagged_object_list(
        request,
        queryset_or_model=Item.objects.published(),
        tag=tag,
        extra_context={
            "rss_feed_url": reverse("lifestream_tag_feeds", kwargs={"tag": tag}),
        }
    )

@require_http_methods(['GET', 'HEAD'])
def search(request):
    # Get unique keywords
    raw_keywords = request.GET.get("q") or ""
    domain = request.GET.get("domain")
    keywords = list(set((raw_keywords).split()))
    if keywords: 
        queryset = Item.objects.published()
        for keyword in keywords:
            queryset = queryset.filter(Q(title__icontains=keyword) | Q(clean_content__icontains=keyword))
        if domain:
            queryset = queryset.filter(feed__domain=domain)
    else:
        #queryset = Item.objects.none()
        return HttpResponseRedirect(reverse('main_page'))

    return object_list(
        request,
        template_name='lifestream/item_search.html',
        queryset=queryset,
        extra_context={
            'keywords': raw_keywords,
        },
    )
