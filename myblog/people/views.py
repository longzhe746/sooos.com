from django.db.models import Count
from django.shortcuts import render
from django.http import Http404
# Create your views here.
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from myblog.settings import NUM_COMMENT_PER_PAGE, NUM_TOPICS_PER_PAGE
from question.models import *
from django.core.cache import cache
from django.utils import timezone
import datetime


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

        hot_topics=[]
        for comment in comments:
            topic = Topic.objects.get(id=comment['topic'])
            hot_topics.append(topic)
        cache.set('index_hot_topics',hot_topics,60)
    return render()
