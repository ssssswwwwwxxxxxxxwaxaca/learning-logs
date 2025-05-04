from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from learning_logs.models import Topic, Entry,StudySession,LearningGoal
# Create your models here.
class AnalyticsPreferences(models.Model):
    """用户的数据分析偏好设置"""
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='analytics_preferences')
    show_study_time=models.BooleanField(default=True,verbose_name='显示学习时间')
    show_topic_progress=models.BooleanField(default=True,verbose_name='显示主题进度')
    show_goal_progress=models.BooleanField(default=True,verbose_name='显示学习目标进度')
    chart_color_theme=models.CharField(max_length=50,default='default')
    dashboard_layout=models.CharField(max_length=20,default='grid')
    created_at=models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    updated_at=models.DateTimeField(auto_now=True,verbose_name='更新时间')
    
    def __str__(self):
        return f"{self.user.username}的分析偏好设置"
    
class StudyMetric(models.Model):
    """存储用户的每日学习指标汇总"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='study_metrics')
    date = models.DateField()
    total_study_time = models.DurationField(default=timedelta(0))  # 当天总学习时间
    topics_studied = models.PositiveIntegerField(default=0)  # 学习的主题数
    entries_created = models.PositiveIntegerField(default=0)  # 创建的条目数
    goals_completed = models.PositiveIntegerField(default=0)  # 完成的目标数
    ai_interactions = models.PositiveIntegerField(default=0)  # AI交互次数
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        verbose_name = 'Study Metric'
        verbose_name_plural = 'Study Metrics'
        
    def __str__(self):
        return f"{self.user.username}'s metrics for {self.date}"
    
class TopicAnalytics(models.Model):
    """存储每一个主题的学习数据"""
    topic=models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='analytics')
    last_calculated=models.DateField(auto_now=True,verbose_name='最后计算时间')
    total_study_time=models.DurationField(default=timedelta(0),verbose_name='总学习时间')
    study_frequency=models.PositiveIntegerField(default=0,verbose_name='学习频率')
    entry_count=models.PositiveIntegerField(default=0,verbose_name='条目数')
    avg_entry_length=models.FloatField(default=0.0,verbose_name='平均条目长度')
    last_studied=models.DateField(null=True,blank=True,verbose_name='最后学习时间')
    created_at=models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    
    class Meta:
        verbose_name='Topic Analytics'
        verbose_name_plural='Topic Analytics'
        
    def __str__(self):
        return f"Analytics for {self.topic.text}"
    
    
    def days_since_last_studied(self):
        """计算自上次学习的天数"""
        if not self.last_studied:
            return None
        return (timezone.now()-self.last_studied).days
    
    def get_study_frequency(self):
        """计算学习频率"""
        if self.study_frequency <0.25:
            return 'Very Low'
        elif self.study_frequency<1:
            return 'Low'
        elif self.study_frequency<2:
            return 'Moderate'
        elif self.study_frequency<4:
            return 'High'
        else:
            return 'Very High'
        
        
class LearningStreak(models.Model):
    """记录用户的学习连续性"""
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='learning_streaks')
    current_streak=models.PositiveIntegerField(default=0,verbose_name='当前连续学习天数')
    longest_streak=models.PositiveIntegerField(default=0,verbose_name='最长连续学习天数')
    last_activity_date=models.DateField(null=True,blank=True,verbose_name='最后活动日期')
    created_at=models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    updated_at=models.DateTimeField(auto_now=True,verbose_name='更新时间')
    
    def __str__(self):
        return f"{self.user.username}'s learning streak"
    
    def update_streak(self,activity_date=None):
        """更新学习连续性"""
        if activity_date is None:
            activity_date=timezone.now().date()
        
        """如果是第一次学习记录"""
        if self.last_activity_date is None:
            self.current_streak=1
            self.longest_streak=1
            self.last_activity_date=activity_date
            self.save()
            return
        """如果是连续学习"""
        days_diff=(activity_date-self.last_activity_date).days
        if days_diff==0:
            return 
        elif days_diff==1:
            self.current_streak+=1
            if self.current_streak>self.longest_streak:
                self.longest_streak=self.current_streak
        elif days_diff>1:
            self.current_streak=1
        self.last_activity_date=activity_date
        self.save()


class ProductivityTime(models.Model):
    """记录用户的学习的生产力数据"""
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='productivity_times')
    hour_of_day=models.PositiveIntegerField(verbose_name='小时')
    total_duration=models.DurationField(default=timedelta(0),verbose_name='总时长')
    session_count=models.PositiveSmallIntegerField(default=0,verbose_name='会话数')
    avg_productivity=models.FloatField(default=0.0,verbose_name='平均生产力')
    created_at=models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    updated_at=models.DateTimeField(auto_now=True,verbose_name='更新时间')
    
    class Meta:
        unique_together=['user', 'hour_of_day']
    def __str__(self):
        return f"{self.user.username}'s productivity at {self.hour_of_day}:00"
    
    def get_productivity_level(self):
        """获取生产力水平"""
        if self.avg_productivity<0.25:
            return 'Very Low'
        elif self.avg_productivity<0.5:
            return 'Low'
        elif self.avg_productivity<0.75:
            return 'Moderate'
        else:
            return 'High'
        
class LearningInsight(models.Model):
    """系统生成的学习洞察与建议"""
    INSIGHT_TYPES=[
        ('productivity','生产力洞察'),
        ('pattern','学习模式洞察'),
        ('recommendation', '学习建议'),
        ('achievement', '成就提醒'),
        ('streak', '连续性'),
        ('general', '一般信息'),
    ]
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='learning_insights')
    insight_type=models.CharField(max_length=20,choices=INSIGHT_TYPES,verbose_name='洞察类型')
    title=models.CharField(max_length=100,verbose_name='标题')
    message=models.TextField(verbose_name='内容')
    is_read=models.BooleanField(default=False,verbose_name='已读')
    is_important=models.BooleanField(default=False,verbose_name='重要')
    created_at=models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    
    class Meta:
        ordering=['-created_at']
    def __str__(self):
        return f"{self.user.username}'s insight: {self.title}"
    
class AnalyticsReport(models.Model):
    """定期生成的学习分析报告"""
    REPORT_TYPES = (
        ('daily', '每日报告'),
        ('weekly', '每周报告'),
        ('monthly', '每月报告'),
        ('yearly', '年度报告'),
        ('custom', '自定义报告'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analytics_reports')
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    title = models.CharField(max_length=100)
    summary = models.TextField()
    period_start = models.DateField()
    period_end = models.DateField()
    total_study_time = models.DurationField()
    topics_covered = models.PositiveIntegerField()
    entries_created = models.PositiveIntegerField()
    goals_completed = models.PositiveIntegerField()
    data_json = models.JSONField(null=True, blank=True)  # 存储报告的详细数据
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-period_end']
    
    def __str__(self):
        return f"{self.user.username}'s {self.get_report_type_display()}: {self.title}"
    
    def get_study_time_hours(self):
        """将学习时间转换为小时"""
        return round(self.total_study_time.total_seconds() / 3600, 1)