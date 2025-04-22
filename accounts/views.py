from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout as auth_logout
from .models import CustomUser  # 导入自定义用户模型
from .forms import CustomUserChangeForm, CustomUserCreationForm  # 合并导入

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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('learning_logs:index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def logout(request):
    if request.method == 'POST':
        auth_logout(request)
        return redirect('learning_logs:index')
    else:
        return render(request, 'accounts/logout.html')

@login_required
def profile(request):
    """ 处理头像上传 """
    if request.method == "POST":
        avatar = request.FILES.get('avatar_url')
        if avatar:
            user = request.user
            user.avatar_url = avatar  # 确保模型中存在此字段
            user.save()
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('learning_logs:index')
        else:
            return render(request, 'accounts/login.html', {'error': '用户名或密码错误'})
    return render(request, 'accounts/login.html')