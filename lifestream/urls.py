from django.conf.urls.defaults import *
from django.contrib import admin

from lifestream.rss import *

admin.autodiscover()

urlpatterns = patterns('django.views.generic.simple',
    url(r'^page/0?1$', 'redirect_to', {'url': '/'}, name="page_one"),
)

urlpatterns += patterns('lifestream.views',
    url(r'^$', 'main_page', name='main_page'),
    url(r'^page/(?P<page>\d+)$', 'main_page', name='main_page_paged'),
    url(r'^items/view/(?P<item_id>\d+)$', 'item_page', name='item_page'),
)

feeds = {
  'recent': RecentItemsFeed,
}

urlpatterns += patterns('',
  url(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds }, name='lifestream_feeds'), 
)
