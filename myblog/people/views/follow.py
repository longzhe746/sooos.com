from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from people.models import Member,Follower
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError

@csrf_protect
@login_required
def follow(request,uid):
    if request.method == 'GET':
        return HttpResponseRedirect(reverse('question:index'))
    user_a = request.user
    try:
        user_b = Member.objects.get(pk=uid)

    except Member.DoesNotExist:
        messages.error(request,'用户不存在')
        return HttpResponseRedirect(reverse('question:index'))

    if user_a.id == uid:
        messages.error(request,'不能关注自己')
        return HttpResponseRedirect(reverse('question:index'))
    try:
        follow = Follower.objects.create(user_a=user_a,user_b=user_b)
        messages.success(request,'关注成功')
    except IntegrityError:
        messages.error(request, '你已经关注了该用户.')
        return HttpResponseRedirect(reverse('question:index'))

@csrf_protect
@login_required
def un_follow(request,uid):
    if request.method == 'GET':
        return HttpResponseRedirect(reverse('question:index'))
    user_a = request.user
    try:
        user_b = Member.objects.get(pk=uid)
        follower = Follower.objects.filter(user_a=user_a,user_b=user_b).first()

    except (Member.DoesNotExist,Follower.DoesNotExist):
        messages.error(request,'粉丝关系或用户不存在')
        return HttpResponseRedirect(reverse('question:index'))
    else:
        follower.delete()
        messages.success(request,'取消关注成功')
        return HttpResponseRedirect(reverse('user:user',args=(user_b.id,)))

@login_required
def following(request):
    following_list = Follower.objects.filter(user_a=request.user).all()
    return render(request,'people/following.html',{'following_list':following_list})