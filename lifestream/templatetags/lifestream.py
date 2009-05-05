#!/usr/bin/env python
#:coding=utf-8:
#:tabSize=2:indentSize=2:noTabs=true:
#:folding=explicit:collapseFolds=1:

from datetime import datetime,timedelta

from django.utils.safestring import mark_safe
from django.utils.translation import ngettext,ugettext_lazy as _
from django.template import Node, Library, TemplateDoesNotExist, TemplateSyntaxError, Variable
from django.template.loader import render_to_string

register = Library()

@register.simple_tag
def item_class(item):
  return item.feed.domain.replace(".", "-") 

@register.filter
def friendly_date(date, include_time=False):
  """
  Prints a human friendly date.
  """
  delta = datetime.now() - date
   
  if delta < timedelta(seconds=60):
    msg = _("Just now")
  elif delta < timedelta(seconds=60*60):
    minutes = delta.seconds / 60
    msg = ngettext('%(minutes)s minute ago',
            '%(minutes)s minutes ago', minutes) % {
      'minutes': minutes,
    }
  elif delta < timedelta(days=1):
    hours = int(delta.seconds / 60.0 / 60)
    msg = ngettext('%(hours)s hour ago',
            '%(hours)s hours ago', hours) % {
      'hours': hours,
    }
  elif delta < timedelta(days=7):
    msg = ngettext('%(days)s day ago',
            '%(days)s days ago', delta.days) % {
      'days': delta.days,
    }
  elif delta < timedelta(days=31):
    weeks = int(delta.days / 7)
    msg = ngettext('%(weeks)s week ago',
            '%(weeks)s weeks ago', weeks) % {
      'weeks': weeks,
    }
  elif delta < timedelta(days=365):
    months = int(delta.days / 31)
    msg = ngettext('%(months)s month ago',
            '%(months)s months ago', months) % {
      'months': months,
    }
  else:
    years = int(delta.days / 365)
    msg = ngettext('%years)s year ago',
            '%(years)s years ago', years) % {
      'years': years,
    }
  return mark_safe(msg)

class LifestreamItemNode(Node):
    def __init__(self, item_var):
        self.item_var = Variable(item_var)

    def render(self, context):
        item = self.item_var.resolve(context)
        context["item"] = item
        try:
            template_name = "lifestream/sites/%s.html" % item_class(item)
            return render_to_string(template_name, context)
        except TemplateDoesNotExist, e:
            template_name = "lifestream/sites/basic.html"
            return render_to_string(template_name, context)

@register.tag
def render_item(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("%r takes one argument." % bits[0])
    return LifestreamItemNode(bits[1])

@register.filter
def urlize_twitter(text):
    import re
    return mark_safe(re.sub(r'@([a-zA-Z0-9_]*)', r'@<a href="http://twitter.com/\1">\1</a>', text))
