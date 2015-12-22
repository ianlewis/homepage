#:coding=utf-8:

from django.conf import settings


def debug(request):
    return {
        'debug': settings.DEBUG,
    }


def disqus(request):
    return {
        'disqus_shortname': settings.DISQUS_WEBSITE_SHORTNAME,
        'disqus_api_key': settings.DISQUS_API_KEY,
    }
