#!/usr/bin/python3
# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404
from people.forms import RegisterForm, LoginForm
from people.models import Member, Follower, EmailVerified as Email, FindPass
from question.models import Topic, Comment
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.utils import timezone
from django.core.cache import cache
from myblog.settings import NUM_TOPICS_PER_PAGE, NUM_COMMENT_PER_PAGE
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.mail import send_mail
import datetime
from django.contrib.auth import logout as auth_logout, authenticate, login as auth_login

SITE_URL = settings.SITE_URL


@csrf_protect
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            new_user = Member.create_user(username=data['username'],
                                          email=data['email'],
                                          password=data['password'])

            new_user.save()

            email_verified = Email(user=new_user)
            email_verified.token = email_verified.generate_token()
            email_verified.save()

            # email_verified -> 邮箱验证函数
            send_mail("欢迎加入", "%s 你好：\r\n请点击链接验证你的邮箱：%s%s，" % (
                new_user.username, SITE_URL, reverse('user:email_verified', args=(new_user.id, email_verified.token))),
                      "1599940638@qq.com", [data['email']])
            messages.success(request,'恭喜注册成功，请去您的邮箱验证。如果查不到邮件，那么可以垃圾邮箱中查收以下。')
            # *******check django 函数验证登录用户名和密码 *************
            user = authenticate(email=data['email'],password=data['password'])
            # login
            auth_login(request,user)

            go = reverse('question:index')

            is_auto_login = request.POST.get('auto')
            if not is_auto_login:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(60)

            return HttpResponseRedirect(go)
    else:
        form = RegisterForm()
    return render(request,'people/register.html',{'form':form})

@csrf_protect
def login(request):

    if request.user.is_authenticated():
        # 从那儿来就返回到那个页面
        return HttpResponseRedirect(request.META.get('HTTP_PEFERER','/'))

    # POST
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data['username']

            if '@' in username:
                email = username
            else:
                try:
                    user = Member.objects.get(username=username)
                except Member.DoesNotExist:
                    messages.error(request, '用户名和密码错误。')
                    return render(request, 'people/login.html', locals())
                else:
                    email = user.email

            user = authenticate(email=email,password=data['password'])

            if user is not None:
                auth_login(request,user)
                go = reverse('question:index')
                is_auto_login = request.POST.get('auto')
                if not is_auto_login:
                    request.session.set_expiry(0)
                return HttpResponseRedirect(go)
            else:
                messages.error(request,'用户名和密码错误。')
                return render(request,'people/login.html',locals())

    # GET
    else:
        form = LoginForm()
        return render(request, 'people/login.html', locals())
@login_required
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('question:index'))

# 用户棒
def au_top(request):
    au_list = cache.get('au_top_list')
    if not au_list:
        au_list = Member.objects.order_by('-au')[:20]
        cache.set('au_top_list',au_list,60)
    user_count = cache.get('au_top_list')
    if not user_count:
        user_count = Member.objects.all().count()
        cache.set('user_count', user_count, 60)

    return render(request,'people/au_top.html',locals())

def user(request,uid):
    user_from_id = Member.objects.get(pk=uid)
    user_a = request.user
    if user_a.is_authenticated():
        try:
            follower = Follower.objects.filter(user_a=user_a,user_b=user_from_id)
        except Follower.DoesNotExist:
            follower = None

    topic_list = Topic.objects.order_by('-created_on').filter(author=user_from_id.id)[:NUM_TOPICS_PER_PAGE]
    comment_list = Comment.objects.order_by('-created_on').filter(author=user_from_id.id)[:NUM_TOPICS_PER_PAGE]
    return render(request,'people/user.html',locals())

def user_topics(request,uid):
    this_user = Member.objects.get(pk=uid)
    topic_list = Topic.objects.order_by('-created_on').filter(author=uid)
    paginator = Paginator(topic_list,NUM_TOPICS_PER_PAGE)

    page = request.GET.get('page')
    try:
        topic_list = paginator.page(page)
    except PageNotAnInteger:
        topic_list = paginator.page(1)
    except EmptyPage:
        topic_list = paginator.page(paginator.num_pages)

    return  render(request,'people/user_topics.html',locals())

def user_comments(request,uid):
    this_user = Member.objects.get(pk=uid)
    comment_list = Comment.objects.filter(author=uid).order_by('-created_on')
    paginator = Paginator(comment_list, NUM_COMMENT_PER_PAGE)

    page = request.GET.get('page')
    try:
        comment_list = paginator.page(page)
    except PageNotAnInteger:
        comment_list = paginator.page(1)
    except EmptyPage:
        comment_list = paginator.page(paginator.num_pages)

    return render(request, 'people/user_comments.html', locals())


@login_required
@csrf_protect
def send_verified_email(request):
    if request.method == 'GET':
        return HttpResponseRedirect(reverse('user:settings'))
    user = request.user
    if user.email_verified:
        messages.error(request,'您的邮箱已经验证过了.')
        return HttpResponseRedirect(reverse('user:settings'))
    try:
        last_email = Email.objects.get(user=user)

    except Email.DoesNotExist:
        pass

    if (timezone.now() - last_email.timestamp).seconds < 60:
        messages.error(request, '一分钟之内只能申请一次.')
    else:
        try:
            email = Email.objects.get(user=user)
            email.token = email.generate_token()
            email.timestamp = timezone.now()
            email.save()
        except Email.DoesNotExist:
            email = Email(user=user)
            email.token = email.generate_token()
            email.save()

        finally:
            send_mail("欢迎加入", "%s 你好：\r\n请点击链接验证你的邮箱：%s%s，" % (
                user.username, SITE_URL, reverse('user:email_verified', args=(user.id, email.token))),
                      "1599940638@qq.com", [user.email])
            messages.success(request, '恭喜注册成功，请去您的邮箱验证。如果查不到邮件，那么可以垃圾邮箱中查收以下。')

    return HttpResponseRedirect(reverse('user:settings'))

def email_verified(request,uid,token):
    try:
        user = Member.objects.get(pk=uid)
        email = Email.objects.get(user=user)
    except Member.DoesNotExist:
        raise Http404
    except Email.DoesNotExist:
        raise Http404

    else:
        if email.token == token:
            user.email_verified = True
            user.save()
            email.delete()
            messages.success(request,'验证成功')
            if not request.user.is_authenticated():
                auth_login(request.user)
            return  HttpResponseRedirect(reverse('question:index'))
        else:
            raise Http404


def find_password(request):
    if request.method == 'GET':
        return render(request,'people/find_password.html')
    email = request.POST.get['email']
    user = None
    try:
        user = Member.objects.get(email=email)
    except Member.DoesNotExist:
        messages.error(request,'未找到用户')

    find_pass= FindPass.objects.filter(user=user)
    if find_pass:
        find_pass = find_pass[0]
        if (timezone.now() - find_pass.timestamp).seconds < 60:
            messages.error(request,'一分钟内不可以重复找回密码.')
            return HttpResponseRedirect(reverse('people:login'))
        else:
            find_pass = FindPass(user=user)
            find_pass.token=find_pass.generate_token()
            find_pass.save()

        send_mail("重置密码",
                  "%s 你好：\r\n请点击链接重置密码:：%s%s，" % (
                      user.username, SITE_URL, reverse('user:first_reset_password', args=(user.id, ))),
                  "1599940638@qq.com",
                  [user.email])
        messages.success(request, '恭喜注册成功，请去您的邮箱验证。如果查不到邮件，那么可以垃圾邮箱中查收以下。')























