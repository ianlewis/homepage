#:coding=utf-8:

from django.conf.urls import url, include

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from homepage.blog import urls as blog_urls
from homepage.core import views

import redirects

admin.autodiscover()

urlpatterns = redirects.urlpatterns

urlpatterns += [
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'accounts/', include('django.contrib.auth.urls')),
]

urlpatterns += blog_urls.urlpatterns

urlpatterns += [
    url(r'robots.txt', views.robots, name='robots'),
    url(r'favicon.ico', views.favicon, name='favicon'),
    url(r'_status/version', views.version, name='version'),
    url(r'^$', views.main_page, name='main_page'),
]
