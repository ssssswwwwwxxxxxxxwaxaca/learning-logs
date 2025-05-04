from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # 现有的 URL 配置
    path('', views.dashboard, name='dashboard'),
    path('statistics/', views.study_statistics, name='statistics'),
    path('progress/', views.progress_report, name='progress'),
    path('topic/<int:topic_id>/', views.topic_analysis, name='topic_analysis'),
    path('preferences/update/', views.update_preferences, name='update_preferences'),
    
    # 添加缺少的 chart_data URL 映射
    path('api/chart/', views.get_chart_data, name='chart_data'),
    
    # 添加缺失的 API 端点 URL 配置
    path('api/monthly-stats/', views.api_monthly_stats, name='api_monthly_stats'),
    path('api/weekly-stats/', views.api_weekly_stats, name='api_weekly_stats'),
    path('api/hourly-stats/', views.api_hourly_stats, name='api_hourly_stats'),
    path('api/topic-stats/', views.api_topic_stats, name='api_topic_stats'),
    path('api/calendar-data/', views.api_calendar_data, name='api_calendar_data'),
    path('api/topic-trend/<int:topic_id>/', views.api_topic_trend, name='api_topic_trend'),
    path('api/topic-comparison/<int:topic_id>/', views.api_topic_comparison, name='api_topic_comparison'),
    path('api/entry-length/<int:topic_id>/', views.api_entry_length, name='api_entry_length'),
    
    # 资源管理
    path('resource/add/<int:topic_id>/', views.add_resource, name='add_resource'),
]