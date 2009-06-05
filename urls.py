from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings

from blog import urls as blog_urls
import redirects

admin.autodiscover()

urlpatterns = redirects.urlpatterns

urlpatterns += blog_urls.urlpatterns

urlpatterns += patterns('',
    
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    # Uncomment the next line to enable the admin:
    url(r'^admin/update_feeds', 'lifestream.admin_views.admin_update_feeds', name='admin_update_feeds'),
    (r'^admin/(.*)', admin.site.root),
    
    (r'', include('lifestream.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
