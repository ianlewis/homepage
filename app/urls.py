from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.conf import settings

from blog import urls as blog_urls
from lifestream.rss import RecentItemsFeed
from lifestream.models import Lifestream,Item
from tagging.models import Tag,TaggedItem

import redirects

admin.autodiscover()

urlpatterns = redirects.urlpatterns

urlpatterns += patterns('',
    (r'^admin/filebrowser/', include('filebrowser.urls')),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
 
    (r'accounts/', include('django.contrib.auth.urls')),
    #(r'^hg/', include('hgwebproxy.urls')),
)

urlpatterns += blog_urls.urlpatterns

urlpatterns += patterns('',
    url(r'^$', 'homepage.views.main_page', name='main_page'), 
    url(r'^items/tag/(?P<tag>.+)$', 'homepage.views.tag_page', name='tag_page'),

    url(r'^items/view/(?P<item_id>\d+)$', 'homepage.views.item_page', name='lifestream_item_page'),
    url(r'^items/site/(?P<domain>.+)$', 'homepage.views.domain_page', name='lifestream_domain_page'),

    url(r'^items/search$', 'homepage.views.search', name='lifestream_item_search'),
)

class HomepageRecentItemsFeed(RecentItemsFeed):

    def link(self, obj):
        return reverse('main_page')

    def item_link(self, item):
        return reverse('lifestream_item_page', kwargs={
            'item_id': item.id,
        })

    def get_object(self, bits):
        return Lifestream.objects.get(pk=1)

class TaggedItemsFeed(RecentItemsFeed):

    def link(self, obj):
        return reverse('tag_page', kwargs={'tag': obj.name })

    def item_link(self, item):
        return reverse('lifestream_item_page', kwargs={
            'item_id': item.id,
        })

    def items(self, obj):
        return TaggedItem.objects.get_by_model(Item.objects.published(), obj)

    def get_object(self, bits):
        if len(bits) != 1:
            raise Tag.DoesNotExist
        return Tag.objects.get(name=bits[0])

feeds = {
    'recent': HomepageRecentItemsFeed,
    'tag': TaggedItemsFeed,
}

urlpatterns += patterns('',
    url(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds }, name='lifestream_feeds'), 
)

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
