#:coding=utf8:

from django.contrib.syndication.feeds import Feed
from models import Post

from django.core.urlresolvers import reverse

from tagging.utils import parse_tag_input
from tagging.models import Tag, TaggedItem

class LatestBlogEntries(Feed):
    def link(self, obj):
        if isinstance(obj, Tag):
            return reverse('blog_tag_page', kwargs={
                'locale':self.locale,
                'tag': obj.name,
            })
        else:
            return reverse('blog_page', kwargs={'locale':self.locale})

    def items(self, obj):
        if isinstance(obj, Tag):
            return TaggedItem.objects.get_by_model(Post.objects.published().filter(locale=self.locale), obj)
        else:
            return Post.objects.published().filter(locale=self.locale)[:10]

    def item_author_name(self, item):
        return item.author.get_full_name()

    def item_author_email(self, item):
        return item.author.email

    def item_author_link(self, item):
        return reverse('main_page')

    def item_pubdate(self, item):
        return item.pub_date

    def item_categories(self, item):
        return parse_tag_input(item.tags)

    def get_object(self, bits):
        if len(bits) > 1:
            raise Tag.DoesNotExist
        elif len(bits) == 1:
            return Tag.objects.get(name=bits[0])
        else:
            return None

class LatestEnglishBlogEntries(LatestBlogEntries):
    title="Ian Lewis' Blog"
    description="The latest blog posts from Ian Lewis' blog"
    locale="en"

class LatestJapaneseBlogEntries(LatestBlogEntries):
    title=u"イアンルイスのブログ"
    description=u"イアンルイスのブログの最新エントリ"
    locale="jp"
