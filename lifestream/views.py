#!/usr/bin/env python
#:coding=utf-8:
#:tabSize=2:indentSize=2:noTabs=true:
#:folding=explicit:collapseFolds=1:

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext, Context, loader
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_list,object_detail
from django.core.urlresolvers import reverse
from django.conf import settings

from lifestream.util.decorators import allow_methods

from lifestream.models import *

@allow_methods('GET')
def main_page(request):
  from blog.models import Post

  # Get latest English and Japanese post.
  try:
      en_post = Post.objects.published().filter(locale="en").latest("pub_date")
  except Post.DoesNotExist:
      en_post = None
  try:
      jp_post = Post.objects.published().filter(locale="jp").latest("pub_date")
  except Post.DoesNotExist:
      jp_post = None

  return object_list(request, 
      queryset = Item.objects.published(), 
      template_name = "lifestream/main.html",
      extra_context = {
          "jp_post": jp_post,
          "en_post": en_post,
      }
  )

@allow_methods('GET')
def tag_page(request, tag):
    from tagging.utils import get_tag
    from tagging.models import TaggedItem
    tag_instance = get_tag(tag)
    queryset = TaggedItem.objects.get_by_model(Item.objects.published(), tag_instance)

    return object_list(request, queryset, "lifestream/item_list.html")

@allow_methods('GET')
def domain_page(request, domain):
    return object_list(
        request,
        Item.objects.published().filter(feed__domain=domain),
        "lifestream/item_list.html",
    )

@allow_methods('GET', 'POST')
def item_page(request, item_id=None):
  try:
    item = Item.objects.get(id=item_id,published=True)
  except Item.DoesNotExist:
    raise Http404
  
  return direct_to_template(request, "lifestream/item.html", { 
    "item": item,
  })
