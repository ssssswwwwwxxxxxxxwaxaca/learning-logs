# accounts/models.py
import os
import re
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

class CustomUser(AbstractUser):
    avatar_url = models.ImageField(
        verbose_name="头像",
        upload_to='avatars/',
        blank=True,
        null=True
    )
    
    def save(self, *args, **kwargs):
        if self.avatar_url and hasattr(self.avatar_url, 'name') and self.avatar_url.name:
            # 修复路径问题
            current_path = self.avatar_url.name
            
            # 修正重复的avatars目录
            if 'avatars/avatars/' in current_path:
                self.avatar_url.name = current_path.replace('avatars/avatars/', 'avatars/')
            
            # 确保路径格式正确
            elif not current_path.startswith('avatars/'):
                filename = os.path.basename(current_path)
                self.avatar_url.name = f'avatars/{filename}'
                
            # 处理特殊字符
            filename = os.path.basename(self.avatar_url.name)
            safe_filename = re.sub(r'[^\w\.-]', '_', filename)
            if filename != safe_filename:
                self.avatar_url.name = f'avatars/{safe_filename}'
                
        super().save(*args, **kwargs)