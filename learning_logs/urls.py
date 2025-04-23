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
    
    #搜索的界面
    path('search/',views.search,name='search'),
    
    #删除entry
    path('delete_entry/<int:entry_id>',views.delete_entry,name='delete_entry'),
    
    #添加entry评论
    path('entry/<int:entry_id>/comments/', views.entry_comments, name='entry_comments'),

    #删除topic
    path('delete_topic/<int:topic_id>/', views.delete_topic, name='delete_topic'),

    # 新增URL
    path('dashboard/', views.dashboard, name='dashboard'),
    path('goals/', views.goals, name='goals'),
    path('goals/<int:goal_id>/toggle/', views.toggle_goal, name='toggle_goal'),
    path('topics/<int:topic_id>/start_session/', views.start_session, name='start_session'),
    path('end_session/', views.end_session, name='end_session'),
    
    # 学习路径
    path('learning-paths/', views.learning_paths, name='learning_paths'),
    path('learning-paths/new/', views.new_learning_path, name='new_learning_path'),
    path('learning-paths/<int:path_id>/', views.learning_path_detail, name='learning_path_detail'),
    path('learning-paths/<int:path_id>/delete/', views.delete_learning_path, name='delete_learning_path'),
    # 路径步骤
    path('steps/<int:step_id>/', views.step_detail, name='step_detail'),
    path('steps/<int:step_id>/toggle-completion/', views.toggle_step_completion, name='toggle_step_completion'),
    # 资源
    path('resources/<int:resource_id>/toggle-completion/', views.toggle_resource_completion, name='toggle_resource_completion'),
]