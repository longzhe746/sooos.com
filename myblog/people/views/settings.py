from django.http import HttpResponse, HttpResponseRedirect, Http404
from people.forms import RegisterForm, LoginForm
from people.models import Member, Follower, EmailVerified as Email, FindPass
from question.models import Topic, Comment
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout as auth_logout
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
from django.contrib.auth import logout as auth_logout, authenticate, login

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
            # check
            user = authenticate(email=data['email'],password=data['password'])
            # login
            login(request,user)

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