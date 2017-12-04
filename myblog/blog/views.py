from django.shortcuts import render,redirect
from blog.forms import UserForm
from django.http import HttpRequest
from django.http import HttpResponse

from . import models


# Create your views here.


def index(request):
    # article = models.Article.objects.get(pk=1) 获取一行
    articles = models.Article.objects.all()
    return render(request, 'blog/index.html', {'articles': articles})
'''
Test Request
'''
def index2(request):
    # article = models.Article.objects.get(pk=1) 获取一行
    articles = models.Article.objects.all()
    return render(request, 'blog/index2.html', {'articles': articles})

def article_page(request, article_id):
    article = models.Article.objects.get(pk=article_id)
    return render(request, 'blog/article_page.html', {'article': article})


def edit_page(request, article_id):
    if str(article_id) == '0':
        return render(request, 'blog/edit_page.html')
    article = models.Article.objects.get(pk=article_id)
    return render(request, 'blog/edit_page.html',{'article':article})

def edit_action(request):
    title = request.POST.get('title', 'TITLE')
    content = request.POST.get('content', 'CONTENT')
    article_id = request.POST.get('article_id', '0')
    if article_id == '0':
        models.Article.objects.create(title=title, content=content)
        articles = models.Article.objects.all()
        return render(request, 'blog/index.html', {'articles': articles})
    article = models.Article.objects.get(pk=article_id)
    article.title = title
    article.content = content
    article.save()
    return render(request, 'blog/article_page.html', {'article': article})

def login(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            password = form.cleaned_data['password']
            user = models.User.objects.filter(user_id__exact=user_id,password__exact=password)
            if user:
                print('登录成功')
                articles = models.Article.objects.all()
                return redirect('/blog/index', {'articles': articles})
            else:
                return HttpResponse("登录ID或密码错误<a href='/blog/login'>登录</a>")

    else:
        form = UserForm().as_ul()
    return render(request, 'blog/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = models.User()
            print(form.cleaned_data)
            user.user_id = form.cleaned_data['user_id']
            user.password = form.cleaned_data['password']

            user.save()
        return login(request)
    else:
        form = UserForm().as_ul()
    return render(request, 'blog/register.html', {'form': form})


