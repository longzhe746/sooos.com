#!/usr/bin/python3
# -*- coding: utf-8 -*-
from django import  template
from django.conf import  settings
import urllib.parse, hashlib
from django.contrib.auth import get_user_model

GRAVATAR_URL_PREFIX = getattr(settings,"GRAVATAR_URL_PREFIX")
GRAVATAR_DEFAULT_IMAGE =getattr(settings,"GRAVATAR_DEFAULT_IMAGE")
GRAVATAR_DEFAULT_RATING =getattr(settings,"GRAVATAR_DEFAULT_RATING")
GRAVATAR_DEFAULT_SIZE =getattr(settings,"GRAVATAR_DEFAULT_SIZE")

User = get_user_model()
register = template.Library()

def _get_user(user):
    if not isinstance(user,User):
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            raise  Exception('Bad user for gravatar.')
    return user.email

def _get_gravatar_id(email):
    email = email.encode()
    return hashlib.md5(email).hexdigest()

@register.simple_tag
def gravatar(user,size=None):
    try:
        if isinstance(user,User):
            return  gravatar_url_for_user(user,size)
        return gravatar_url_for_email(user,size)
    except ValueError:
        raise template.TemplateSyntaxError('语法错误。')

@register.simple_tag
def gravatar_url_for_user(user,size=None):
    if user.avatar and user.avatar != '':
        img = 'http://p1q9bkv61.bkt.clouddn.com/' + user.avatar
        return  img
    else:
        email = _get_user(user)
        return  gravatar_url_for_email(email,size)

@register.simple_tag
def gravatar_url_for_email(user,size=None):
    gravatar_url = '%savatar/%s' %(GRAVATAR_URL_PREFIX,_get_gravatar_id(user.email))

    parameters = [ p for p in (('d',GRAVATAR_DEFAULT_IMAGE),('s',size or GRAVATAR_DEFAULT_SIZE),('g',GRAVATAR_DEFAULT_RATING))if p[1]]
    if parameters:
        gravatar_url += '?' + urllib.parse.urlencode(parameters,doseq=True)
    return  gravatar_url
