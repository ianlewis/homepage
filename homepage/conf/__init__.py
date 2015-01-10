#:coding=utf-8:

import os
import re
import csv
from StringIO import StringIO

from django.core.exceptions import ImproperlyConfigured


def env_var(name, value_type=str, **kwargs):
    if name not in os.environ and 'default' not in kwargs:
        raise ImproperlyConfigured("The %s environment variable "
                                   "is required." % name)

    value = os.environ.get(name, None)
    if value is None:
        # If the environment variable is not set and a default
        # was provided then return it.
        return kwargs['default']

    try:
        if value_type == bool:
            value = _bool(value)
        else:
            value = value_type(value)
    except ValueError, e:
        raise ImproperlyConfigured('The %s environment variable is '
                                   'invalid: "%s".' % (name, e))
    return value


def _bool(value):
    if isinstance(value, basestring):
        if value.lower() == 'false':
            return False
    return bool(value)


def csv_list(value):
    value = list(csv.reader(StringIO(value)))
    if len(value) > 1:
        raise ValueError("The value must contain one line of CSV")
    return value[0]


def email_csv(value):
    csv_values = csv_list(value)
    addresses = []
    for addr in csv_values:
        match = re.match('(.+) <(.+@.+)>|(.+@.+)', addr)
        if match:
            grp = match.groups()
            name = grp[0]
            if name:
                addresses.append((name, grp[1]))
            else:
                addresses.append((grp[2], grp[2]))
        else:
            raise ValueError("The value must be a valid email address.")

    return addresses
