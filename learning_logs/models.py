from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


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

    def __str__(self):
        return self.text

class Entry(models.Model):
    #学到的有关某个主题的具体知识
    topic=models.ForeignKey(Topic,on_delete=models.CASCADE)
    text=models.TextField()
    date_added=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural='entries'
        
    def __str__(self):
        #返回一个简单的字符串表示
        if len(self.text)<50:
            return self.text
        else:
            return f"{self.text[:50]}......"

