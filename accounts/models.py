# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    avatar_url = models.ImageField(  # 重命名字段为 avatar
        verbose_name="头像",
        upload_to='avatars/',   # 文件存储到 media/avatars/ 目录
        blank=True,             # 允许为空
        null=True              # 允许数据库 NULL 值
    )