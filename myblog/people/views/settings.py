from django.http import HttpResponse, HttpResponseRedirect,Http404
from people.forms import  RegisterForm,LoginForm
from people.models import Member,Follower,EmailVerified as Email,FindPass
from question.models import     Topic,Comment
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.utils import timezone
from django.core.cache import  cache
from myblog.settings import NUM_TOPICS_PER_PAGE,NUM_COMMENT_PER_PAGE
from django.conf import settings
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.core.mail import send_mail
import datetime
from django.contrib.auth import logout as auth_logout , authenticate,login

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