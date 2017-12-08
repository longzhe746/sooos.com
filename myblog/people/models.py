#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import string

from django.db import models
from django.contrib.auth.models import  BaseUserManager,AbstractBaseUser
from django.utils import timezone
import hashlib
from django.conf import settings
SALT = getattr(settings,'EMAIL_TOKEN_SALT')
# Create your models here.
class MyUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise  ValueError('Users must have an username')
        now = timezone.now()
        user = self.model(
            username = username,
            email=self.normalize_email(email),
            date_joined=now,
            last_login=now

        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, username, email, password):
        user = self.create_user(username,
                                email,
                                password=password)
        user.is_admin  = True
        user.save(using=self._db)
        return  user

class Member(AbstractBaseUser):
    email = models.EmailField(verbose_name='邮箱',max_length=255,unique=True)
    username = models.CharField(verbose_name='用户名',max_length=16,unique=True)
    weibo_id = models.CharField(verbose_name='新浪微博',max_length=30,blank=True)
    blog = models.CharField(verbose_name='个人网站',max_length=200,blank=True)
    location = models.CharField(verbose_name='城市',max_length=10,blank=True)
    profile = models.CharField(verbose_name='个人简介',max_length=140,blank=True)
    avatar = models.CharField(verbose_name='头像',max_length=128,blank=True)
    au = models.IntegerField(verbose_name='用户活跃度',default=True)
    last_ip = models.IPAddressField(verbose_name='上次访问IP',default='0.0.0.0')
    email_verified = models.BooleanField(verbose_name='邮箱是否验证',default=False)
    date_joined = models.DateTimeField(verbose_name='用户注册时间',default=timezone.now)
    topic_num = models.IntegerField(verbose_name='帖子数',default=0)
    comment_num = models.IntegerField(verbose_name='评论数',default=0)
    is_active = models.BooleanField( default=True)
    is_admin = models.BooleanField( default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    object = MyUserManager()

    def __str__(self):
        return self.username
    def calculate_au(self):
        self.au = self.topic_num * 5 + self.comment_num * 1
        return self.au
    def is_email_verified(self):
        return  self.email_verified

    def get_weibo_id(self):
        return  self.weibo_id

    def get_username(self):
        return self.username

    def get_full_name(self):
        return  self.email

    def get_email(self):
        return  self.email

    def get_short_name(self):
        return self.username

    def has_perm(perm, obj=None):
        return True
    def has_module_perms(self,app_label):
        return  True
    @property
    def is_staff(self):
        return self.is_admin

class Follower(models.Model):
    user_a = models.ForeignKey(Member, related_name='user_a',verbose_name="偶像")
    user_b = models.ForeignKey(Member, related_name='user_b',verbose_name="粉丝")

    class Meta:
        unique_together = ("user_a","user_b")


    def __str__(self):
        return "{} following {}".format(self.user_a,self.user_b)

class EmailVerified(models.Model):
    user = models.OneToOneField(Member,related_name='user')
    token = models.CharField(verbose_name='Email 验证 token',max_length=32,default=None)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return  "%s@%s" % (self.user,self.token)

    def generate_token(self):
        year = self.timestamp.year
        month = self.timestamp.month
        day = self.timestamp.day
        date = '-'.join([year,month,day])
        token = hashlib.md5((self.ran_str()+date).encode('utf-8')).hexdigest()
        return  token

    def ran_str(self):
        salt = ''.join(random.sample(string.ascii_letters + string.digits,8))
        return  SALT+salt

class FindPass(models.Model):
    user = models.OneToOneField(Member, verbose_name='用户')
    token = models.CharField( max_length=32, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def _str__(self):
        return "%s@%s" % (self.user,self.token)

    def generate_token(self):
        year = self.timestamp.year
        month = self.timestamp.month
        day = self.timestamp.day
        date = '-'.join([year,month,day])
        token = hashlib.md5((self.ran_str()+date).encode('utf-8')).hexdigest()
        return  token

    def ran_str(self):
        salt = ''.join(random.sample(string.ascii_letters + string.digits,8))
        return  SALT+salt