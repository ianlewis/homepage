#:coding=utf8:

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.conf import settings

from homepage.blog.models import Post
from homepage.blog.decorators import feed_redirect


class BlogDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(BlogDetail, self).get_context_data(**kwargs)

        locale = context['object'].locale

        context['locale'] = locale
        if locale in settings.RSS_FEED_URLS:
            context['rss_feed_url'] = settings.RSS_FEED_URLS[locale]
        return context

    def get_queryset(self):
        return Post.objects.published().filter(
            locale=self.kwargs['locale'],
        )

blog_detail = require_http_methods(['GET', 'HEAD'])(BlogDetail.as_view())


class BlogDetailPreview(BlogDetail):
    def get_queryset(self):
        return Post.objects.all()


blog_detail_preview = never_cache(
    staff_member_required(
        require_http_methods(['GET', 'HEAD'])(
            BlogDetailPreview.as_view(),
        )
    )
)


class BlogPage(ListView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(BlogPage, self).get_context_data(**kwargs)
        locale = self.kwargs['locale']
        context['locale'] = locale
        if locale in settings.RSS_FEED_URLS:
            context['rss_feed_url'] = settings.RSS_FEED_URLS[locale]
        return context

    def get_queryset(self):
        return Post.objects.published().filter(
            locale=self.kwargs['locale'],
        )

blog_page = require_http_methods(['GET', 'HEAD'])(
    feed_redirect(BlogPage.as_view()),
)


class TagPage(ListView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(TagPage, self).get_context_data(**kwargs)
        locale = self.kwargs['locale']
        tag = self.kwargs['tag']
        context['locale'] = locale
        context['tag'] = tag
        if locale in settings.RSS_FEED_URLS:
            context['rss_feed_url'] = settings.RSS_FEED_URLS[locale]
        return context

    def get_queryset(self):
        return Post.objects.published().filter(
            locale=self.kwargs['locale'],
            tags__name=self.kwargs['tag'],
        )

tag_page = TagPage.as_view()
