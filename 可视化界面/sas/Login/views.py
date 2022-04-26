from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect

from .models import Users


def get_ID():
    IDs = [id.ID for id in Users.objects.all()]
    for i, id in enumerate(IDs):
        if id == (i + 1):
            continue
        else:
            return i + 1
    return len(IDs) + 1


# Create your views here.
def login(request):
    # 用户登录
    if request.method == "POST" and request.POST:
        # 获取用户通过POST提交过来的数据
        usm = request.POST.get('usm')
        pwd = request.POST.get('pwd')
        
        if Users.objects.filter(用户名=usm):
            if Users.objects.filter(用户名=usm)[0].密码 == pwd:
                # TODO: 显示登录成功信息
                return HttpResponseRedirect('/main')
            else:
                return render(request, 'login.html', {'content2': "密码错误！"})
        else:
            return render(request, 'login.html', {'content1': "用户不存在！请先注册。"})
    return render(request, 'login.html')


def register(request):
    # 用户注册
    if request.method == "POST":
        # 获取用户通过POST提交过来的数据
        usm = request.POST.get('usm')
        pwd = request.POST.get('pwd')
        age = request.POST.get('age')
        usertype = request.POST.get('usertype')
        if Users.objects.filter(用户名=usm):
            return render(request, 'register.html', {'content1': "用户名已存在！"})
        
        ID = get_ID()
        try:
            #TODO: 显示注册成功信息
            Users.objects.create(ID=ID, 用户名=usm, 密码=pwd, 年龄=int(age), 身份=usertype)
            return HttpResponseRedirect('/login/')
        except:
            render(request, 'register.html', {'content1': "注册失败！请检查输入是否正确。"})
    return render(request, 'register.html')
