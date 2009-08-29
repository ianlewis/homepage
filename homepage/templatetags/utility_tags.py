#:coding=utf8:

from datetime import datetime,timedelta

from django.utils.safestring import mark_safe
from django.utils.translation import ngettext,ugettext_lazy as _
from django.template.defaultfilters import stringfilter

from django import template
register = template.Library()

@register.filter
def truncate_chars(value, max_length):
    if value is None:
        return ""
    max_length = int(max_length)
    if len(value) > max_length:
        truncd_val = value[:max_length]
        truncd_val = truncd_val.rstrip()
        return truncd_val + "..."
    return value

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
  delta = datetime.utcnow() - date
   
  if delta < timedelta(seconds=60):
    msg = _("Just now")
  elif delta < timedelta(seconds=60*60):
    minutes = delta.seconds / 60
    msg = ngettext('%(minutes)s minute ago',
            '%(minutes)s minutes ago', minutes) % {
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
