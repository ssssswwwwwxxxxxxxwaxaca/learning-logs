from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from learning_logs.models import StudySession, Entry, LearningGoal
from .models import StudyMetric, TopicAnalytics, LearningStreak

@receiver(post_save, sender=StudySession)
def update_analytics_on_study_session(sender, instance, created, **kwargs):
    """当添加或更新学习会话时更新分析数据"""
    user = instance.user
    
    # 更新每日指标
    session_date = instance.start_time.date()
    metric, created = StudyMetric.objects.get_or_create(
        user=user,
        date=session_date,
        defaults={
            'total_study_time': timedelta(0),
            'topics_studied': 0,
            'entries_created': 0,
            'goals_completed': 0,
            'ai_interactions': 0
        }
    )
    
    # 重新计算当天总学习时间
    day_sessions = StudySession.objects.filter(
        user=user,
        start_time__date=session_date
    )
    metric.total_study_time = sum((s.duration for s in day_sessions), timedelta(0))
    
    # 计算学习的不同主题数
    metric.topics_studied = day_sessions.values('topic').distinct().count()
    metric.save()
    
    # 更新主题分析
    topic = instance.topic
    analytics, created = TopicAnalytics.objects.get_or_create(topic=topic)
    analytics.last_studied = timezone.now()
    
    # 计算主题总学习时间
    topic_sessions = StudySession.objects.filter(topic=topic)
    analytics.total_study_time = sum((s.duration for s in topic_sessions), timedelta(0))
    
    # 更新学习频率
    analytics.study_frequency = topic_sessions.count()
    analytics.save()
    
    # 更新学习连续性
    streak, created = LearningStreak.objects.get_or_create(user=user)
    streak.update_streak(session_date)

@receiver(post_save, sender=Entry)
def update_analytics_on_entry(sender, instance, created, **kwargs):
    """当添加或更新条目时更新分析数据"""
    if created:
        topic = instance.topic
        user = topic.owner
        entry_date = instance.date_added.date()
        
        # 更新每日指标
        metric, created = StudyMetric.objects.get_or_create(
            user=user,
            date=entry_date,
            defaults={
                'total_study_time': timedelta(0),
                'topics_studied': 0,
                'entries_created': 0,
                'goals_completed': 0,
                'ai_interactions': 0
            }
        )
        metric.entries_created += 1
        metric.save()
        
        # 更新主题分析
        analytics, created = TopicAnalytics.objects.get_or_create(topic=topic)
        analytics.entry_count = Entry.objects.filter(topic=topic).count()
        
        # 计算平均条目长度
        entries = Entry.objects.filter(topic=topic)
        if entries:
            avg_length = sum(len(e.text) for e in entries) / entries.count()
            analytics.avg_entry_length = avg_length
            
        analytics.save()