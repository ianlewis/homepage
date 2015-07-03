#:coding=utf8:

from django.views.generic.list import ListView
from django.views.generic.list_detail import object_list, object_detail
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache

from .models import Post
from .decorators import feed_redirect


@never_cache
@staff_member_required
@require_http_methods(['GET', 'HEAD'])
def blog_detail_preview(request, object_id):
    object = Post.objects.get(pk=object_id)
    defaults = {
        "queryset": Post.objects.all(),
        "object_id": object_id,
        "extra_context": {
            "locale": object.locale,
            "is_preview": True,
        },
    }
    return object_detail(request, **defaults)


@require_http_methods(['GET', 'HEAD'])
@feed_redirect
def blog_page(request, locale="en"):
    return object_list(
        request,
        Post.objects.published().filter(locale=locale),
        extra_context={
            "locale": locale,
            "rss_feed_url": reverse("blog_feed_%s" % locale),
        },
    )


@require_http_methods(['GET', 'HEAD'])
def blog_detail(request, slug, locale="en"):
    defaults = {
        "queryset": Post.objects.published().filter(locale=locale),
        "slug": slug,
        "extra_context": {"locale": locale},
    }
    return object_detail(request, **defaults)


class TagPage(ListView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(TagPage, self).get_context_data(**kwargs)
        locale = self.kwargs['locale']
        tag = self.kwargs['tag']
        context['rss_feed_url'] = reverse("blog_feed_%s_tag" % locale,
                                          kwargs={"tag": tag})
        return context

    def get_queryset(self):
        return Post.objects.published().filter(
            locale=self.kwargs['locale'],
            tags__name=self.kwargs['tag'],
        )

tag_page = TagPage.as_view()
