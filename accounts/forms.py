from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):  # 新增创建表单
    class Meta:
        model = CustomUser
        fields = ['username', 'email','avatar_url']  # 添加头像字段

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'avatar_url']  # 添加头像字段