from django.conf.urls import  url
from people import  views
import question.views as qus
from people import views
urlpatterns = [
    
    url(r'^my/fav/$',qus.fav_topic_list,name='fav_topic_list'),
    url(r'^follow/(?P<uid>\d+)/$',views.follow,name='follow'),
    url(r'^un_follow/(?P<uid>\d+)/$',views.un_follow,name='un_follow'),
    url(r'^my/following/$',views.following,name='following'),
    url(r'^au_top/$',views.following,name='au_top'),

    url(r'^login/$',views.login,name='login'),
    url(r'^register/$',views.register,name='register'),
    url(r'^logout/$',views.logout,name='logout'),

    url(r'^users/$',views.au_top,name='au_top'),
    url(r'^user/(?P<uid>\d+)/$',views.user,name='user'),
    url(r'^user/(?P<uid>\d+)/topics/$',views.user_topics,name='topic'),
    url(r'^user/(?P<uid>\d+)/comments/$',views.user_comments,name='comments'),
]