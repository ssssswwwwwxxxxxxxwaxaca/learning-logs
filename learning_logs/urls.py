###定义learning_logs的URL模式
from django.urls import path,include 
from .import views

app_name='learning_logs'

urlpatterns = [
    #主页 在应用程序中可能请求的网页
    path('',views.index,name='index'),

    path('topics/',views.topics,name='topics'),
    #显示单个主题及其所有的条目
    path('topic/<int:topic_id>',views.topic,name='topic'),

    #添加新主题的网页
    path('new_topic/',views.new_topic,name='new_topic'),

    #添加新条目的网页的界面
    path('new_entry/<int:topic_id>',views.new_entry,name='new_entry'),

    #新增编辑条目的界面
    path('edit_entry/<int:entry_id>',views.edit_entry,name='edit_entry'),
]