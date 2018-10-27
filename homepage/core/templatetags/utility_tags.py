#:coding=utf8:

import re
import markdown

from datetime import datetime,timedelta

from docutils.writers import html4css1
from docutils.core import publish_parts
from docutils import nodes

from django.utils.safestring import mark_safe
from django.utils.translation import ngettext,ugettext_lazy as _
from django.template.defaultfilters import stringfilter
from django import template

from homepage.core.utils import batch

register = template.Library()

register.filter(batch)

class HTMLWriter(html4css1.Writer):
    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = HTMLTranslator

class HTMLTranslator(html4css1.HTMLTranslator):
    named_tags = []

    def visit_literal(self, node):
        # TODO: wrapping fixes.
        self.body.append("<code>%s</code>" % node.astext())
        raise nodes.SkipNode

def rst_to_html(value):
    parts = publish_parts(source=value, writer=HTMLWriter(),
                          settings_overrides={"initial_header_level": 2})
    return mark_safe(parts["fragment"])
register.filter("rst_to_html", rst_to_html)

def md_to_html(value):
    """
    Convert markdown post to HTML
    """
    return mark_safe(
        markdown.markdown(
            text=value,
            extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite',
                'markdown.extensions.tables',
                'markdown.extensions.smart_strong',
            ],
            extension_configs={
                'markdown.extensions.codehilite': {
                    'css_class': 'highlight',
                }
            }
        )
    )
register.filter("md_to_html", md_to_html)

@register.filter
@stringfilter
def truncate_chars(value, max_length):
    try:
        max_length = int(max_length)
        if len(value.rstrip()) > max_length:
            truncd_val = value[:max_length]
            truncd_val = truncd_val.rstrip()
            return truncd_val + "..."
        return value
    except:
        return ""

def stripentities(value):
    """Strips all HTML entities"""
    from django.utils.html import strip_entities
    return strip_entities(value)
stripentities.is_safe = True
stripentities = stringfilter(stripentities)
register.filter(stripentities)

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
            '%(minutes)s min ago', minutes) % {
      'minutes': minutes,
    }
  elif delta < timedelta(days=1):
    hours = int(delta.seconds / 60 / 60)
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
    msg = ngettext('%(years)s year ago',
            '%(years)s years ago', years) % {
      'years': years,
    }
  return mark_safe(msg)

@register.filter
def cat(value, other_value):
    return "%s%s" % (value, other_value)

@register.filter
def urlize_twitter(text):
    return mark_safe(
        re.sub(r'@([a-zA-Z0-9_]*)', r'@<a href="http://twitter.com/\1">\1</a>',
            re.sub(r'#([a-zA-Z0-9_-]*)', r'<a href="http://twitter.com/#search?q=\1">#\1</a>', text)
        )
    )
