#:coding=utf8:

from django.contrib.syndication.feeds import Feed
from models import Post

from django.core.urlresolvers import reverse

from tagging.utils import parse_tag_input

class LatestEnglishBlogEntries(Feed):
    title="Ian Lewis' Blog"
    description="The latest blog posts from Ian Lewis' blog"

    def link(obj):
        return reverse('blog_page', kwargs={'locale':'en'})

    def items(self, obj):
        return Post.objects.published().filter(locale='en')[:10]

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

class LatestJapaneseBlogEntries(Feed):
    title=u"イアンルイスのブログ"
    description=u"イアンルイスのブログの最新エントリ"
    
    def link(obj):
        return reverse('blog_page', kwargs={'locale':'jp'})

    def items(self, obj):
        return Post.objects.published().filter(locale="jp")[:10]

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
