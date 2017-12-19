#!/usr/bin/python3
# -*- coding: utf-8 -*-
from django.db import models
from people.models import Member as User
from django.db.models.signals import post_save
# Create your models here.
# 类别
class Category(models.Model):
    name = models.CharField(max_length=100,verbose_name='类别名称')
    def __str__(self):
        return self.name
# 节点
class Node(models.Model):
    name = models.CharField(max_length=100,verbose_name='节点名称')
    slug = models.SlugField(max_length=100,verbose_name='url标识符')
    created_on = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    updated_on = models.DateTimeField(blank=True,null=True,auto_now=True,verbose_name='更新时间')
    category = models.ForeignKey(Category,verbose_name='所属类别')
    num_topics = models.IntegerField(default=0, verbose_name='主题数')
    def __str__(self):
        return self.name
# 文章
class Topic(models.Model):
    title = models.CharField(max_length=100,verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    node = models.ForeignKey(Node,verbose_name='所属节点')
    author = models.ForeignKey(User,verbose_name='作者')
    num_views = models.IntegerField(default=0,verbose_name='浏览量')
    num_comments = models.IntegerField(default=0,verbose_name='评论数')
    last_reply = models.ForeignKey(User,related_name='+',verbose_name='最后回复者')
    created_on = models.DateTimeField(auto_now_add=True,verbose_name='发表时间')
    updated_on = models.DateTimeField(blank=True,null=True,verbose_name='发表时间')
    def __str__(self):
        return self.title
# 评论
class Comment(models.Model):
    content = models.TextField(verbose_name='内容')
    author = models.ForeignKey(User,verbose_name='作者')
    topic = models.ForeignKey(Topic,verbose_name='所属主题')
    created_on = models.DateTimeField(auto_now_add=True,verbose_name='评论时间')
    def __str__(self):
        return self.content
# 消息
class Notice(models.Model):
    from_user = models.ForeignKey(User,related_name='+',verbose_name='来自用户')
    to_user = models.ForeignKey(User,related_name='+',verbose_name='接受用户')
    topic = models.ForeignKey(Topic,null=True)
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    is_readed = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
        return self.content
# 收藏的文章
class FavoritedTopic(models.Model):
    user = models.ForeignKey(User, verbose_name='用户')
    topic = models.ForeignKey(Topic,verbose_name='主题')
    def __str__(self):
        return str(self.id)

def create_notice(sender,**kwargs):
    comment = kwargs['instance']
    if comment.author != comment.topic.author:
        Notice.objects.create(from_user=comment.author,
                              to_user=comment.topic.author,
                              topic=comment.topic,
                              content = comment.content)

post_save.connect(create_notice,sender=Comment)

















