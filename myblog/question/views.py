from django.db.models import Count
from django.shortcuts import render
from django.http import Http404
# Create your views here.
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from myblog.settings import NUM_COMMENT_PER_PAGE, NUM_TOPICS_PER_PAGE
from question.models import *
from question.forms import *
from people.models import Member as User
from django.core.cache import cache
from django.utils import timezone
import datetime
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
import re
from  django.contrib import messages


def index(request):
    # 主题列表
    topic_list = Topic.objects.all().order_by('-created_on')[:NUM_TOPICS_PER_PAGE]
    nodes = cache.get('index_nodes')
    if not nodes:
        nodes = []
        category_List = Category.objects.all()
        for category in category_List:
            node = {}
            category_nodes = Node.objects.filter(category=category.id)
            node['category_name'] = category.name
            node['category_nodes'] = category_nodes
            nodes.append(node)
        cache.set('index_nodes', nodes, 60)  # 一分钟刷新
    # 今日热议
    hot_topics = cache.get('index_hot_topics')
    if not hot_topics:
        now = timezone.now()
        start = now - datetime.timedelta(hours=23, minutes=59, seconds=59)
        comments = Comment.objects.filter(created_on__gt=start).values('topic').annotate(count=Count('topic')).order_by(
            '-count')[:NUM_TOPICS_PER_PAGE]

        hot_topics = []
        for comment in comments:
            topic = Topic.objects.get(id=comment['topic'])
            hot_topics.append(topic)
        cache.set('index_hot_topics', hot_topics, 60)
    return render(request, 'question/index.html', {'topic_list': topic_list, 'nodes': nodes, 'hot_topics': hot_topics})


def recent(request):
    topic_list = Topic.objects.all().order_by('-created_on')
    paginator = Paginator(topic_list, NUM_COMMENT_PER_PAGE)
    page = request.GET.get('page')
    try:
        topic_list = paginator.page(page)
    except PageNotAnInteger:
        topic_list = paginator.page(1)
    except EmptyPage:
        topic_list = paginator.page(paginator.num_pages)  # 最后一页

    return render(request, 'question/recent.html', {'topic_list': topic_list})


def node(request, node_slug):
    try:
        node = Node.objects.get(slug=node_slug)
    except Node.DoesNotExist:
        raise Http404

    topic_list = Topic.objects.filter(node=node).order_by('-created_on')
    paginator = Paginator(topic_list, NUM_COMMENT_PER_PAGE)
    page = request.GET.get('page')
    try:
        topic_list = paginator.page(page)
    except PageNotAnInteger:
        topic_list = paginator.page(1)
    except EmptyPage:
        topic_list = paginator.page(paginator.num_pages)  # 最后一页

    return render(request, 'question/node.html', {'topic_list': topic_list, 'node': node})


def topic(request, topic_id):
    try:
        topic = Topic.objects.get(id=topic_id)
    except Topic.DoesNotExist:
        raise Http404

    topic.num_views += 1
    topic.save()

    faved_num = FavoritedTopic.objects.filter(topic=topic).count()
    if request.user.is_authenticated():
        try:
            faved_topic = FavoritedTopic.objects.filter(user=request.user, topic=topic)
        except (User.DoesNotExist, FavoritedTopic.DoesNotExist):
            faved_topic = None

    comment_list = Comment.objects.filter(topic=topic).order_by('created_on')
    paginator = Paginator(comment_list, NUM_COMMENT_PER_PAGE)
    page = request.GET.get('page')
    try:
        comment_list = paginator.page(page)
    except PageNotAnInteger:
        comment_list = paginator.page(1)
    except EmptyPage:
        comment_list = paginator.page(paginator.num_pages)  # 最后一页

    form = ReplyForm()
    return render(request, 'question/topic.html', locals())


@login_required
def reply(request, topic_id):
    try:
        topic = Topic.objects.get(id=topic_id)
        comment_list = Comment.objects.filter(topic=topic).order_by('created_on')
        paginator = Paginator(comment_list, NUM_COMMENT_PER_PAGE)
        page = request.GET.get('page')
        if page == None:
            page = paginator.num_pages
        try:
            comment_list = paginator.page(page)
        except PageNotAnInteger:
            comment_list = paginator.page(1)
        except EmptyPage:
            comment_list = paginator.page(paginator.num_pages)  # 最后一页

    except Topic.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            last_comment = Comment.objects.filter(author=request.user).order_by('-created_on')[:1]
            last_comment = last_comment.first()

            if last_comment and last_comment.content == form.cleaned_data['content'] and (
                (timezone.now() - last_comment.created_on).seconds < 5):
                messages.error(request,'你是否正在尝试连续提交两次重复的回复？')
            else:
                comment = form.save(commit=False)
                request.user.comment += 1
                request.user.calculate_au()
                request.user.save()
                comment.author =request.user

                try:
                    topic = Topic.objects.get(id=topic_id)
                except Topic.DoesNotExist:
                    raise  Http404
                comment.topic = topic
                comment.save()

                #@ 正则
                team_name_pattern = re.compile('(?<=@)([0-9a-zA-Z_.]+)',re.UNICODE) # re.UNICODE 匹配中文
                at_name_list = set(re.findall(team_name_pattern,comment.content))
                if at_name_list:
                    