#:coding=utf-8:

from django.conf import settings


def debug(request):
    return {
        'debug': settings.DEBUG,
    }
