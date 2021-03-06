from django.db.models import Count
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
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
from django.contrib import messages


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
                messages.error(request, '你是否正在尝试连续提交两次重复的回复？')
            else:
                comment = form.save(commit=False)
                request.user.comment_num += 1
                request.user.calculate_au()
                request.user.save()
                comment.author = request.user

                try:
                    topic = Topic.objects.get(id=topic_id)
                except Topic.DoesNotExist:
                    raise Http404
                comment.topic = topic
                comment.save()

                # @ 正则
                team_name_pattern = re.compile('(?<=@)([0-9a-zA-Z_.]+)', re.UNICODE)  # re.UNICODE 匹配中文
                at_name_list = set(re.findall(team_name_pattern, comment.content))
                if not at_name_list:
                    pass
                for at_name in at_name_list:
                    if at_name != comment.author.username and at_name != comment.topic.author.username:
                        continue
                    try:
                        at_user = User.objects.get(username=at_name)
                        notice = Notice(from_user=comment.author, to_user=at_user, topic=comment.topic,
                                        content=comment.content)
                    except:
                        pass
                topic.num_comments += 1
                topic.updated_on = timezone.now()
                topic.last_reply = request.user
                topic.save()
                return HttpResponseRedirect(reverse('question:topic', args=(topic_id,)))


    else:
        form = ReplyForm()
    content = {'node': node, 'topic': topic, 'form': form, 'comment_list': comment_list, 'paginator': paginator}
    return render(request, 'question/topic.html', content)


@login_required
def new(request, node_slug):
    try:
        node = Node.objects.get(slug=node_slug)
    except Node.DoesNotExist:
        raise Http404
    # post
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            last_topic = Topic.objects.filter(author=request.user).order_by('-created_on')[:1]
            last_topic = last_topic.first()
            if last_topic and \
                    last_topic.title == form.cleaned_data['title'] and (
                    (timezone.now() - last_topic.created_on).seconds < 5):

                messages.error(request, '你是否正在尝试连续提交两次重复的内容？')
                return HttpResponseRedirect(reverse('question:topic', args=(last_topic.id,)))
            else:
                topic = form.save(commit=False)
                topic.node = node
                request.user.topic_num += 1
                request.user.calculate_au()
                request.user.save()
                topic.author = request.user
                topic.last_reply = request.user
                topic.created_on = timezone.now()
                topic.save()
                node.num_topics += 1
                node.save()
                # 跳转页面
                return HttpResponseRedirect(reverse('question:topic', args=(topic.id,)))
    # get
    else:
        form = TopicForm()
    return render(request,'question/new.html',{'node':node,'form':form})

@login_required
def edit(request,topic_id):
    try:
        topic = Topic.objects.get(id=topic_id)
        if topic.author != request.user:
            raise  Http404

    except Topic.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic.title = form.cleaned_data['title']
            topic.content = form.cleaned_data['content']
            topic.updated_on = timezone.now()
            topic.save()

        return HttpResponseRedirect(reverse('question:topic',args=(topic_id,)))

    else:
        form = TopicForm(instance=topic)

    return  render(request,'question/edit.html',{'topic':topic,'form':form})

@login_required
def notice(request):
    context = {}
    if request.method == 'GET':
        notices = Notice.objects.filter(to_user=request.user,is_deleted=False).order_by('time')
        context['notices'] = notices
        return  render(request,'question/notice.html',context)

@login_required
def notice_delete(request,notice_id):
        if request.method == 'GET':
            try:
                notice = Notice.objects.get(id=notice_id)
            except Notice.DoesNotExist:
                raise Http404

            notice.is_deleted = True
            notice.save()

            return  HttpResponseRedirect(reverse('question:notice'))

@login_required
def fav_topic_list(request):
    faved_topic = FavoritedTopic.objects.filter(user=request.user).all()
    return render(request,'question/fav_topic.html',locals())



@login_required
def fav_topic(request,topic_id):
    if request.method == 'GET':
        return HttpResponseRedirect(reverse('question:index'))
    try:
        topic = Topic.objects_get(pk=topic_id)
        if FavoritedTopic.objects.filter(user=request.user,topic=topic).first():
            messages.error(request,'主题你已经关注了。')
        # method 1
        # fav_topic_new = FavoritedTopic.objects.create(user=request.user,topic=topic)
        # method 2
        fav_topic_new = FavoritedTopic(user=request.user,topic=topic)
        fav_topic_new.save()

    except Topic.DoesNotExist:
        messages.error(request,'主题不存在')
        return  HttpResponseRedirect(reverse('question:index'))

    return HttpResponseRedirect(reverse('question:topic', args=(topic_id,)))


@login_required
def unfav_topic(request,topic_id):
    if request.method == 'GET':
        return HttpResponseRedirect(reverse('question:index'))
    try:
        topic = Topic.objects_get(pk=topic_id)
        faved_topic = FavoritedTopic.objects.filter(user=request.user,topic=topic)
        faved_topic.delete()
    except Topic.DoesNotExist:
        messages.error(request,'主题不存在')
        return HttpResponseRedirect(reverse('question:index'))
    return HttpResponseRedirect(reverse('question:topic', args=(topic_id,)))








