#:coding=utf8:

"""
Implementation of the RSS feeds for the blog.
"""

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse

from homepage.blog.templatetags.blog_tags import to_lead
from homepage.blog.models import Post, Tag


class LatestBlogEntries(Feed):
    """
    A base class used for RSS feeds. This class supports
    adding a tag argument on the URL which will limit
    the resulting posts to the posts with the given tag.
    """
    def link(self, obj):
        if isinstance(obj, Tag):
            return reverse('blog_tag_page', kwargs={
                'locale': self.locale,
                'tag': obj.name,
            })
        else:
            return reverse('blog_page', kwargs={'locale': self.locale})

    def items(self, obj):
        if isinstance(obj, Tag):
            return Post.objects.published().filter(
                locale=self.locale,
                tags=obj,
            )
        else:
            return Post.objects.published().filter(locale=self.locale)[:10]

    def item_author_name(self, item):
        return item.author.get_full_name()

    def item_author_email(self, item):
        return item.author.email

    def item_author_link(self, item):
        return reverse('main_page')

    def item_description(self, item):
        return to_lead(item)

    def item_pubdate(self, item):
        return item.pub_date

    def item_categories(self, item):
        return [t.name for t in item.tags.all()]

    def get_object(self, request, tag=None):
        if tag:
            return Tag.objects.get(name=tag)
        else:
            return None


class LatestEnglishBlogEntries(LatestBlogEntries):
    title = "Ian Lewis' Blog"
    description = "The latest blog posts from Ian Lewis' blog"
    locale = "en"


class LatestJapaneseBlogEntries(LatestBlogEntries):
    title = u"イアンルイスのブログ"
    description = u"イアンルイスのブログの最新エントリ"
    locale = "jp"
