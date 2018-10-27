#:coding=utf8:

from django.http import HttpResponsePermanentRedirect
from django.conf import settings

def feed_redirect(view):
    """
    A decorator that redirects based on some old legacy
    parameters. Some folks still subscribe to old feed
    urls.
    """
    def wrapped(request, *args, **kwargs):
        if request.GET.get("tempskin") == "_rss" or \
           request.GET.get("tempskin") == "_rss2" or \
           request.GET.get("tempskin") == "_atom":
            if request.GET.get("lang") == "ja-JP" or \
               kwargs.get("locale") == "jp":
                return HttpResponsePermanentRedirect(settings.RSS_FEED_URLS["jp"])
            else:
                return HttpResponsePermanentRedirect(settings.RSS_FEED_URLS["en"])
        return view(request, *args, **kwargs)

    return wrapped


