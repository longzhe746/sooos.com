#!/usr/bin/python3
# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),  # ^开始 $结束
    url(r'^index/$', views.index),  # ^开始 $结束
    url(r'^index_test/$', views.index2),  # ^开始 $结束
    url(r'^article/(?P<article_id>[0-9]+)/$', views.article_page, name='article_page'),
    url(r'^edit_page/(?P<article_id>[0-9]+)/$', views.edit_page, name='edit_page'),
    url(r'^edit/action/$', views.edit_action, name='edit_action'),
    url(r'^login/$', views.login, name='login'),
    url(r'^register/$', views.register, name='register'),
]
