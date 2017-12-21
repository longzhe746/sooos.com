#!/usr/bin/python3
# -*- coding: utf-8 -*-
from django.conf.urls import  url
from question import  views

urlpatterns = [
    url(r'^$', views.index,name='index'),  # ^开始 $结束
    url(r'^recent/?$',views.recent,name='recent'),
    url(r'^node/(?P<node_slug>[\w-]+)/$',views.node,name='node'),
    url(r'^topic/(?P<topic_id>\d+)/$',views.topic,name='node'),
    url(r'^t/(\d+)/reply/?$',views.reply,name='reply'),
    url(r'^node/([\w-]+)/new/?$',views.new,name='new'),
    url(r'^t/(\d+)/edit/?$',views.edit,name='edit'),

    url(r'^notice/?$',views.notice,name='notice'),
    url(r'^notice/(\d+)/delete/?$',views.notice_delete,name='notice_delete'),

    url(r'^t/fav/(?P<topic_id>\d+)/$',views.fav_topic,name='fav_topic'),
    url(r'^t/unfav/(?P<topic_id>\d+)/$',views.unfav_topic,name='unfav_topic'),

        ]