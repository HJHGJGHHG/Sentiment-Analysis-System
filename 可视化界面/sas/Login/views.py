from django.shortcuts import render
from django.http import HttpResponse

from .models import Users


# Create your views here.
def login(request):
    # 用户登录
    if request.method == "POST":
        # 获取用户通过POST提交过来的数据
        usm = request.POST.get('usm')
        pwd = request.POST.get('pwd')
        
        if Users.objects.filter(用户名=usm):
            if Users.objects.filter(用户名=usm)[0].密码 == pwd:
                return HttpResponse('登录成功')
            else:
                return HttpResponse('密码错误')
        else:
            HttpResponse('用户不存在')
    return render(request, 'login.html')


def register(request):
    # 用户注册
    if request.method == "POST":
        # 获取用户通过POST提交过来的数据
        usm = request.POST.get('usm')
        pwd = request.POST.get('pwd')
        
        if Users.objects.filter(用户名=usm):
            if Users.objects.filter(用户名=usm)[0].密码 == pwd:
                return HttpResponse('登录成功')
            else:
                return HttpResponse('密码错误')
        else:
            HttpResponse('用户不存在')
    return render(request, 'register.html')
