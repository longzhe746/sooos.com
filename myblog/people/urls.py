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

    url(r'^send_verified_email/$',views.send_verified_email,name='send_verified_email'),
    url(r'^email_verified/(?P<uid>\d+)/(?P<token>\w+)/$',views.email_verified,name='email_verified'),
    url(r'^find_password/$',views.find_password,name='find_pass'),
    url(r'^reset_password/(?P<uid>\d+)/(?P<token>\w+)/$',views.first_reset_password,name='first_reset_password'),
    url(r'^reset_password/$',views.reset_password,name='reset_password'),
    #reset_password
    url(r'^settings/$',views.profile,name='settings'),
    url(r'^password/$',views.password,name='password'),

    url(r'^settings/upload_headimage/$', views.upload_headimage, name='upload_headimage'),
    url(r'^settings/delete_headimage/$', views.delete_headimage, name='delete_headimage'),
]