from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, ChangePasswordForm


def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role', 'user')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 选了管理员登录但账号不是管理员
            if role == 'admin' and not user.is_staff:
                messages.error(request, '该账号不是管理员，请选择管理员登录。')
                return render(request, 'registration/login.html', {'form': type('F', (), {'errors': True})()})
            # 选了用户登录但账号是管理员
            if role == 'user' and user.is_staff:
                messages.error(request, '该账号是管理员，请选择管理员登录。')
                return render(request, 'registration/login.html', {'form': type('F', (), {'errors': True})()})
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, '用户名或密码错误，请重试。')
            return render(request, 'registration/login.html', {'form': type('F', (), {'errors': True})()})

    return render(request, 'registration/login.html', {})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = request.POST.get('role', 'user')
            if role == 'admin':
                user.is_staff = True
                user.save()
            login(request, user)
            messages.success(request, '注册成功！')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '密码修改成功，请重新登录！')
            return redirect('login')
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})
