# -*- coding: utf-8 -*-

from django.urls import re_path as url

from news.views import news_detail, news_list

urlpatterns = [
    url(r"^$", news_list, name="news_list"),
    url(r"^(?P<slug>[\w\-]+)/$", news_detail, name="news_detail"),
]
