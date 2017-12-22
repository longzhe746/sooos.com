from django.conf.urls import  url
from people import  views
import question.views as qus
from people import views
urlpatterns = [
    
    url(r'^my/fav/$',qus.fav_topic_list,name='fav_topic_list'),
    url(r'^follow/(?P<uid>\d+)/$',views.follow,name='follow'),
    url(r'^un_follow/(?P<uid>\d+)/$',views.un_follow,name='un_follow'),
    url(r'^my/following/$',views.following,name='following'),
]