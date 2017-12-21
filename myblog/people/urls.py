from django.conf.urls import  url
from people import  views
import question.views as qus

urlpatterns = [
        url(r'^my/fav/$',qus.fav_topic_list,name='fav_topic_list'),
]