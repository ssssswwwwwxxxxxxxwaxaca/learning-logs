from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone

User=get_user_model()
# Create your models here.
class Topic(models.Model):
    """用户学习的主题"""
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        get_user_model(),  # 使用动态获取的用户模型
        on_delete=models.CASCADE,
        verbose_name="所有者"
    )
    total_items = models.IntegerField(default=0)
    completed_items = models.IntegerField(default=0)

    def update_progress(self):
        """更新话题的进度"""
        entries = self.entry_set.all()
        self.total_items = entries.count()
        self.completed_items = entries.filter(completed=True).count()
        self.save()

    def progress_percentage(self):
        """计算完成百分比"""
        if self.total_items == 0:
            return 0
        return int((self.completed_items / self.total_items) * 100)

    def __str__(self):
        return self.text

class Entry(models.Model):
    """对某个主题的具体学习内容"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)  # 添加此字段
    
    class Meta:
        verbose_name_plural = 'entries'
        
    def __str__(self):
        """返回模型的字符串表示"""
        if len(self.text) > 50:
            return f"{self.text[:50]}..."
        return self.text

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # 当条目状态改变时，更新话题进度
        self.topic.update_progress()

class Comment(models.Model):
    entry = models.ForeignKey('Entry', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 使用动态用户模型
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.entry}"
    
class LearningGoal(models.Model):
    """用户学习目标模型"""
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='learning_goals')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_date = models.DateField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def days_remaining(self):
        """返回距离目标日期还有多少天"""
        if self.completed:
            return 0
        return (self.target_date - timezone.now().date()).days
    
    
class StudySession(models.Model):
    """记录学习时长的模型"""
    user = models.ForeignKey(
        get_user_model(),  # 使用动态获取的用户模型
        on_delete=models.CASCADE,
        related_name='study_sessions'
    )
    topic = models.ForeignKey(
        'Topic', 
        on_delete=models.CASCADE,
        related_name='study_sessions'
        )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        """自动计算学习时长"""
        if self.start_time and self.end_time:
            self.duration = self.end_time - self.start_time
        super().save(*args, **kwargs)

class LearningPath(models.Model):
    """用户创建的学习路径"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_hours = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    def get_progress(self):
        """计算学习路径的完成进度"""
        steps = self.pathstep_set.all()
        if not steps:
            return 0
            
        completed_steps = steps.filter(is_completed=True).count()
        return int(completed_steps / steps.count() * 100)
        

class PathStep(models.Model):
    """学习路径中的步骤"""
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    estimated_hours = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return f"{self.path.title} - Step {self.order}: {self.topic.text}"


class StepResource(models.Model):
    """学习步骤的资源"""
    TYPE_CHOICES = (
        ('book', '书籍'),
        ('video', '视频'),
        ('article', '文章'),
        ('exercise', '练习'),
        ('other', '其他')
    )
    
    step = models.ForeignKey(PathStep, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    url = models.URLField(blank=True)
    resource_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other')
    is_completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return self.title
    
    
class AIInteraction(models.Model):
    """存储用户与AI助手的交互"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    question = models.TextField()
    response = models.TextField()
    interaction_type = models.CharField(max_length=20,
        choices=[
        ('question', 'Question'),
        ('summary', 'Summary'),
        ('quiz', 'Quiz'),
        ('recommendation', 'Recommendation')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    model_used=models.CharField(max_length=50,default='llama3')
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.interaction_type}: {self.question[:50]}"


class AIInteraction(models.Model):
    """存储用户与AI助手的交互"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    question = models.TextField()
    response = models.TextField()
    interaction_type = models.CharField(max_length=20, choices=[
        ('question', 'Question'),
        ('summary', 'Summary'),
        ('quiz', 'Quiz'),
        ('recommendation', 'Recommendation')
    ])
    model_used = models.CharField(max_length=50, default='llama3')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.interaction_type}: {self.question[:50]}"