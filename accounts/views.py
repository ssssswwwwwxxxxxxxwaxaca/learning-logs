from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout as auth_logout  # 导入 Django 的内置 logout 函数，并重命名避免冲突
from .forms import CustomUserChangeForm

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('learning_logs:index')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def logout(request):
    if request.method == 'POST':
        auth_logout(request)  # 使用 Django 的内置 logout 函数
        return redirect('learning_logs:index')  # 重定向到 index 页面
    else:
        return render(request, 'accounts/logout.html')
