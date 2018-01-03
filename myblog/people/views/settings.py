from django.http import HttpResponse, HttpResponseRedirect, Http404
from people.forms import RegisterForm, LoginForm,ProfileForm,PasswordChangeForm
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

import base64
import json
from qiniu import   Auth
import qiniu.config
from qiniu import BucketManager
SITE_URL = getattr(settings,'SITE_URL')

AK = 'OJ3ce7xg6u30wsSoWUNV8h1F9h_78Plgwe6C-oNw'
SK = 'pLhnIwlP7eynOLge1Er_sqYNvpKKnH9PqIjmO4bI'

@csrf_protect
@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST,instance=user)
        if form.is_valid():
            form.save(commit=True)
            messages.success(request,'设置已更新')
            return render(request,'people/settings.html')
    else:
        form = ProfileForm(instance=user)

    q = Auth(AK,SK)
    buket_name = 'sooos'
    key_name = 'avatar/' + user.username
    returnBody = '{"name":$(fname), "key":$(key)}'
    returnUrl = SITE_URL + reverse('user:upload_headimage')
    mimeLimit = 'image/jpeg;image/png'
    policy = {
        'returnUrl':returnUrl,
        'returnBody':returnBody,
        'mimeLimit':mimeLimit,

    }

    uptoken = q.upload_token(buket_name,key_name,3600,policy)
    return render(request,'people/settings.html',  {'form':form,'user':user,'uptoken':uptoken}  )

@csrf_protect
@login_required
def password(request):
    user=request.user
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            data = form.clean()
            if user.check_password(data['old_password']):
                user.setpassword(data['password'])
                user.save()
                messages.success(request,'密码设置成功，请重新登录。')
                auth_logout(request)
                return HttpResponseRedirect(reverse('user:login'))
            else:
                messages.error(request,'当前密码输入错误。')
                return render(request,'people/password.html',{'form':form})
    else:
        form = PasswordChangeForm()

    return render(request, 'people/password.html', {'form': form})

#upload_headimgae
@csrf_protect
@login_required
def upload_headimage(request):
    user = request.user
    if request.method == 'POST':
        print(request.GET)
        try:
            retstr = request.GET.get('upload_ret')
            retstr = retstr.encode('utf-8')
            dec = base64.urlsafe_b64decode(retstr)
            ret = json.loads(dec)
            if ret and ret['key']:
                request.user.avatar = ret['key']
                print(ret['key'])
                request.user.save()
            else:
                raise Http404
            messages.success(request,'头像上传成功')
        except:
            messages.error(request,'头像上传失败')
    return HttpResponseRedirect(reverse('user:settings'))


@csrf_protect
@login_required
def delete_headimage(request):
    user = request.user

    if user.avatar == None or user.avatar=='':
        messages.error(request,'你还没有上传头像')
    else:
        q = Auth(AK,SK)
        buket = BucketManager(q)
        buket_name = 'avatar'
        ret,info = buket.delete(buket_name,user.avatar)
        if ret is None:
            messages.error(request,'头像删除失败')
        else:
            user.avatar = ''
            user.save()
            messages.success(request,'头像删除成功')

    return HttpResponseRedirect(reverse('user:settings'))
