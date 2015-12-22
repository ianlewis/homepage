#:coding=utf-8:

from django.conf.urls import url, patterns, include

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from blog import urls as blog_urls

import redirects

admin.autodiscover()

urlpatterns = redirects.urlpatterns

urlpatterns += patterns(
    '',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    (r'accounts/', include('django.contrib.auth.urls')),
)

urlpatterns += blog_urls.urlpatterns

urlpatterns += patterns(
    'homepage.core.views',
    url(r'robots.txt', 'robots', name='robots'),
    url(r'favicon.ico', 'favicon', name='favicon'),
    url(r'^$', 'main_page', name='main_page'),
)
