#!/usr/bin/env python
#:coding=utf-8:
#:tabSize=2:indentSize=2:noTabs=true:
#:folding=explicit:collapseFolds=1:

from django import template
register = template.Library()

@register.simple_tag
def item_class(item):
  return item.feed.domain.replace(".", "-") 
