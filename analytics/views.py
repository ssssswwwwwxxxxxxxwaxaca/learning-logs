from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, F
from django.utils import timezone
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta

from .models import (
    AnalyticsPreferences, StudyMetric, TopicAnalytics, 
    LearningStreak, ProductivityTime, LearningInsight, 
    AnalyticsReport
)
from learning_logs.models import Topic, Entry, StudySession, LearningGoal

@login_required
def dashboard(request):
    """显示分析仪表板"""
    # 获取或创建用户的分析偏好
    preferences, created = AnalyticsPreferences.objects.get_or_create(user=request.user)
    
    # 获取用户的主题
    topics = Topic.objects.filter(owner=request.user)
    
    # 获取总学习时间
    total_study_time = StudySession.objects.filter(
        user=request.user
    ).aggregate(total=Sum('duration'))['total'] or timedelta(0)
    
    # 获取本周学习时间
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    weekly_study_time = StudySession.objects.filter(
        user=request.user,
        start_time__date__gte=week_start
    ).aggregate(total=Sum('duration'))['total'] or timedelta(0)
    
    # 获取主题分析数据
    topic_analytics = TopicAnalytics.objects.filter(topic__owner=request.user).order_by('-total_study_time')[:5]
    
    # 获取最近的学习洞察
    insights = LearningInsight.objects.filter(user=request.user)[:3]
    
    context = {
        'preferences': preferences,
        'topic_count': topics.count(),
        'total_study_time': total_study_time,
        'weekly_study_time': weekly_study_time,
        'topic_analytics': topic_analytics,
        'insights': insights,
    }
    
    return render(request, 'analytics/dashboard.html', context)

@login_required
def study_statistics(request):
    """显示用户的学习时间统计页面"""
    # 获取基本统计数据
    weekly_study_time = StudySession.objects.filter(
        user=request.user,
        start_time__date__gte=timezone.now().date() - timedelta(days=7)
    ).aggregate(total=Sum('duration'))['total'] or timedelta(0)
    
    monthly_study_time = StudySession.objects.filter(
        user=request.user,
        start_time__date__gte=timezone.now().date() - timedelta(days=30)
    ).aggregate(total=Sum('duration'))['total'] or timedelta(0)
    
    # 获取学习连续天数
    streak = LearningStreak.objects.filter(user=request.user).first() or {'current_streak': 0, 'longest_streak': 0}
    
    # 获取最近学习会话
    recent_sessions = StudySession.objects.filter(
        user=request.user
    ).order_by('-start_time')[:10]
    
    context = {
        'weekly_study_time': weekly_study_time,
        'monthly_study_time': monthly_study_time,
        'streak': streak,
        'recent_sessions': recent_sessions,
        'best_hour': 0, # 临时数据，实际应该计算
    }
    
    return render(request, 'analytics/study_statistics.html', context)

@login_required
def topic_analysis(request, topic_id):
    """主题分析详情"""
    topic = get_object_or_404(Topic, id=topic_id, owner=request.user)
    
    # 获取或创建主题分析数据
    analytics, created = TopicAnalytics.objects.get_or_create(topic=topic)
    
    # 获取该主题的学习会话
    sessions = StudySession.objects.filter(user=request.user, topic=topic).order_by('-start_time')
    
    # 获取该主题的条目
    entries = Entry.objects.filter(topic=topic).order_by('-date_added')
    
    context = {
        'topic': topic,
        'analytics': analytics,
        'sessions': sessions,
        'entries': entries,
    }
    
    return render(request, 'analytics/topic_analysis.html', context)

@login_required
def progress_report(request):
    """显示学习进度报告"""
    # 获取所有主题及其进度
    topics = Topic.objects.filter(owner=request.user).annotate(
        entry_count=Count('entry')
    )
    
    # 获取学习目标完成情况
    goals = LearningGoal.objects.filter(user=request.user)
    completed_goals = goals.filter(completed=True).count()
    goal_completion_rate = (completed_goals / goals.count() * 100) if goals.count() > 0 else 0
    
    # 获取最近一个月的学习报告
    today = timezone.now().date()
    month_ago = today - timedelta(days=30)
    recent_reports = AnalyticsReport.objects.filter(
        user=request.user,
        period_start__gte=month_ago
    ).order_by('-created_at')
    
    context = {
        'topics': topics,
        'goals': goals,
        'completed_goals': completed_goals,
        'goal_completion_rate': goal_completion_rate,
        'recent_reports': recent_reports,
    }
    
    return render(request, 'analytics/progress_report.html', context)

@login_required
def update_preferences(request):
    """更新用户分析偏好设置"""
    if request.method == 'POST':
        preferences, created = AnalyticsPreferences.objects.get_or_create(user=request.user)
        
        # 更新偏好设置
        preferences.show_study_time_chart= request.POST.get('show_study_time') == 'on'
        preferences.show_topic_progress = request.POST.get('show_topic_progress') == 'on'
        preferences.show_goal_progress = request.POST.get('show_goal_progress') == 'on'
        preferences.chart_color_theme = request.POST.get('chart_color_theme', 'default')
        preferences.dashboard_layout = request.POST.get('dashboard_layout', 'grid')
        preferences.save()
        
        return redirect('analytics:dashboard')
    
    return redirect('analytics:dashboard')

@login_required
def get_chart_data(request):
    """返回图表数据的API"""
    chart_type = request.GET.get('type', 'daily')
    
    if chart_type == 'daily':
        # 获取最近30天的数据
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        
        metrics = StudyMetric.objects.filter(
            user=request.user,
            date__gte=thirty_days_ago
        ).order_by('date')
        
        labels = []
        study_times = []
        
        # 生成每一天的数据点
        current = thirty_days_ago
        while current <= today:
            labels.append(current.strftime('%m-%d'))
            
            # 查找当天的指标
            metric = metrics.filter(date=current).first()
            if metric:
                hours = round(metric.total_study_time.total_seconds() / 3600, 1)
                study_times.append(hours)
            else:
                study_times.append(0)
                
            current += timedelta(days=1)
            
        return JsonResponse({
            'labels': labels,
            'datasets': [{
                'label': '学习时间 (小时)',
                'data': study_times,
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1
            }]
        })
    
    elif chart_type == 'topics':
        # 获取主题分布数据
        topic_analytics = TopicAnalytics.objects.filter(
            topic__owner=request.user
        ).order_by('-total_study_time')[:8]  # 限制显示数量
        
        labels = []
        data = []
        
        for analytics in topic_analytics:
            labels.append(analytics.topic.text)
            data.append(round(analytics.total_study_time.total_seconds() / 3600, 1))
            
        return JsonResponse({
            'labels': labels,
            'datasets': [{
                'label': '各主题学习时间 (小时)',
                'data': data,
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                ],
                'borderWidth': 1
            }]
        })

@login_required
def api_monthly_stats(request):
    """返回按月统计的学习时间数据"""
    # 获取过去12个月的数据
    today = timezone.now().date()
    months_ago = today - timedelta(days=365)  # 大约一年前
    
    # 按月查询学习时间
    study_sessions = StudySession.objects.filter(
        user=request.user,
        start_time__date__gte=months_ago
    )
    
    # 按月份组织数据
    monthly_data = {}
    for session in study_sessions:
        month_key = session.start_time.strftime('%Y-%m')
        month_name = session.start_time.strftime('%Y年%m月')
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                'name': month_name,
                'duration': timedelta(0)
            }
        monthly_data[month_key]['duration'] += session.duration
    
    # 转换为列表格式，按月份排序
    sorted_months = sorted(monthly_data.keys())
    labels = [monthly_data[month]['name'] for month in sorted_months]
    values = [monthly_data[month]['duration'].total_seconds() / 3600 for month in sorted_months]
    
    return JsonResponse({
        'labels': labels,
        'values': values
    })

@login_required
def api_weekly_stats(request):
    """返回按周统计的学习时间数据"""
    # 获取过去12周的数据
    today = timezone.now().date()
    weeks_ago = today - timedelta(days=84)  # 大约12周前
    
    study_sessions = StudySession.objects.filter(
        user=request.user,
        start_time__date__gte=weeks_ago
    )
    
    # 按周组织数据（使用ISO周格式）
    weekly_data = {}
    for session in study_sessions:
        # 使用ISO周格式 (年-周数)
        week_key = session.start_time.strftime('%G-W%V')
        week_name = f"{session.start_time.strftime('%m/%d')}周"
        
        if week_key not in weekly_data:
            weekly_data[week_key] = {
                'name': week_name,
                'duration': timedelta(0)
            }
        weekly_data[week_key]['duration'] += session.duration
    
    # 转换为列表格式，按周排序
    sorted_weeks = sorted(weekly_data.keys())
    labels = [weekly_data[week]['name'] for week in sorted_weeks]
    values = [weekly_data[week]['duration'].total_seconds() / 3600 for week in sorted_weeks]
    
    return JsonResponse({
        'labels': labels,
        'values': values
    })

@login_required
def api_hourly_stats(request):
    """返回按小时分布的学习时间数据"""
    # 获取最近30天的数据
    today = timezone.now().date()
    days_ago = today - timedelta(days=30)
    
    study_sessions = StudySession.objects.filter(
        user=request.user,
        start_time__date__gte=days_ago
    )
    
    # 初始化所有小时的数据为0
    hourly_data = {str(hour): 0 for hour in range(24)}
    
    # 计算每个小时的学习分钟数
    for session in study_sessions:
        hour = session.start_time.hour
        hourly_data[str(hour)] += session.duration.total_seconds() / 60
    
    # 转换为列表格式
    labels = [f"{hour}:00" for hour in range(24)]
    values = [hourly_data[str(hour)] for hour in range(24)]
    
    return JsonResponse({
        'labels': labels,
        'values': values
    })

@login_required
def api_topic_stats(request):
    """返回主题学习时间分布数据"""
    sort = request.GET.get('sort', 'time')  # 默认按时间排序
    
    # 获取用户的所有主题
    topics = Topic.objects.filter(owner=request.user)
    
    # 获取每个主题的学习时间
    topic_data = []
    for topic in topics:
        study_time = StudySession.objects.filter(
            user=request.user,
            topic=topic
        ).aggregate(total=Sum('duration'))['total'] or timedelta(0)
        
        topic_data.append({
            'name': topic.text,
            'duration': study_time
        })
    
    # 排序
    if sort == 'time':
        topic_data.sort(key=lambda x: x['duration'], reverse=True)
    elif sort == 'name':
        topic_data.sort(key=lambda x: x['name'])
    
    # 提取前10个主题，其他合并为"其他"
    if len(topic_data) > 10:
        top_topics = topic_data[:10]
        others_duration = sum((item['duration'] for item in topic_data[10:]), timedelta(0))
        if others_duration > timedelta(0):
            top_topics.append({
                'name': '其他',
                'duration': others_duration
            })
        topic_data = top_topics
    
    # 转换为前端所需格式
    labels = [item['name'] for item in topic_data]
    values = [item['duration'].total_seconds() / 3600 for item in topic_data]
    
    return JsonResponse({
        'labels': labels,
        'values': values
    })

@login_required
def api_calendar_data(request):
    """返回日历视图所需的每日学习数据"""
    # 获取最近30天的数据
    today = timezone.now().date()
    days_ago = today - timedelta(days=90)  # 获取3个月数据供日历使用
    
    # 查询每日学习时间
    study_sessions = StudySession.objects.filter(
        user=request.user,
        start_time__date__gte=days_ago
    )
    
    # 按天汇总学习时间
    daily_data = {}
    for session in study_sessions:
        day_key = session.start_time.strftime('%Y-%m-%d')
        if day_key not in daily_data:
            daily_data[day_key] = timedelta(0)
        daily_data[day_key] += session.duration
    
    # 转换为前端所需格式
    calendar_data = []
    for day_key, duration in daily_data.items():
        calendar_data.append({
            'date': day_key,
            'study_time_hours': duration.total_seconds() / 3600
        })
    
    return JsonResponse(calendar_data, safe=False)

@login_required
def api_topic_trend(request, topic_id):
    """返回特定主题的学习时间趋势"""
    topic = get_object_or_404(Topic, id=topic_id, owner=request.user)
    range_param = request.GET.get('range', 'month')  # 默认显示一个月
    
    # 根据范围参数计算起始日期
    today = timezone.now().date()
    if range_param == 'month':
        start_date = today - timedelta(days=30)
    elif range_param == 'quarter':
        start_date = today - timedelta(days=90)
    elif range_param == 'year':
        start_date = today - timedelta(days=365)
    else:  # 'all'
        # 使用第一个会话的日期或一年前
        first_session = StudySession.objects.filter(
            user=request.user, 
            topic=topic
        ).order_by('start_time').first()
        start_date = first_session.start_time.date() if first_session else (today - timedelta(days=365))
    
    # 查询该主题的学习会话
    study_sessions = StudySession.objects.filter(
        user=request.user,
        topic=topic,
        start_time__date__gte=start_date
    )
    
    # 按日期组织数据
    daily_data = {}
    for session in study_sessions:
        day_key = session.start_time.strftime('%Y-%m-%d')
        if day_key not in daily_data:
            daily_data[day_key] = timedelta(0)
        daily_data[day_key] += session.duration
    
    # 转换为列表格式
    sorted_days = sorted(daily_data.keys())
    labels = sorted_days
    values = [daily_data[day].total_seconds() / 3600 for day in sorted_days]
    
    return JsonResponse({
        'labels': labels,
        'values': values
    })

@login_required
def api_topic_comparison(request, topic_id):
    """返回主题与相关主题的比较数据"""
    topic = get_object_or_404(Topic, id=topic_id, owner=request.user)
    
    # 简单实现：获取用户的所有主题作为"相关主题"
    # 实际应用中可能需要更复杂的相关性算法
    topics = Topic.objects.filter(owner=request.user)[:5]  # 限制为5个主题
    
    labels = [t.text for t in topics]
    values = []
    
    for t in topics:
        study_time = StudySession.objects.filter(
            user=request.user,
            topic=t
        ).aggregate(total=Sum('duration'))['total'] or timedelta(0)
        values.append(study_time.total_seconds() / 3600)
    
    return JsonResponse({
        'labels': labels,
        'values': values
    })

@login_required
def api_entry_length(request, topic_id):
    """返回主题条目长度分布数据"""
    topic = get_object_or_404(Topic, id=topic_id, owner=request.user)
    
    # 获取该主题的所有条目
    entries = Entry.objects.filter(topic=topic)
    
    # 对条目长度进行分类
    length_categories = {
        '短 (<100字)': 0,
        '中 (100-500字)': 0,
        '长 (500-1000字)': 0,
        '很长 (>1000字)': 0
    }
    
    for entry in entries:
        length = len(entry.text)
        if (length < 100):
            length_categories['短 (<100字)'] += 1
        elif (length < 500):
            length_categories['中 (100-500字)'] += 1
        elif (length < 1000):
            length_categories['长 (500-1000字)'] += 1
        else:
            length_categories['很长 (>1000字)'] += 1
    
    return JsonResponse({
        'labels': list(length_categories.keys()),
        'values': list(length_categories.values())
    })

@login_required
def add_resource(request, topic_id):
    """添加学习资源"""
    topic = get_object_or_404(Topic, id=topic_id, owner=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        url = request.POST.get('url')
        resource_type = request.POST.get('type', 'website')
        description = request.POST.get('description', '')
        
        # 这里假设您有一个 Resource 模型
        # Resource.objects.create(
        #     topic=topic,
        #     user=request.user,
        #     title=title,
        #     url=url,
        #     type=resource_type,
        #     description=description
        # )
        
        # 如果没有 Resource 模型，可以先注释此部分
        
    return redirect('analytics:topic_analysis', topic_id=topic.id)