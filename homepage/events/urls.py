#:coding=utf8:

from django.conf.urls import url

from homepage.events import views

urlpatterns = [
    url(r'^talks/?$', views.talk_list, name="talk_list"),
    url(r'^talks/(?P<slug>[^/]+)/?$', views.talk_detail, name='talk_detail'),
]
