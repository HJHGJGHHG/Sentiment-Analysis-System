import json
from django.contrib import messages
from django.shortcuts import render, redirect

import sys

sys.path.append("../")
from Login.models import Users

# Create your views here.
def main(request):
    cookies = request.COOKIES
    try:
        username = json.loads(cookies.get("username"))
        usertype = json.loads(cookies.get("usertype"))
    except TypeError:
        # 未登录，跳转到登录界面
        return redirect('/login')
    return render(request, 'index.html', {'username': username, 'usertype': usertype})


def profile(request):
    bio = "长度不超过200字符"
    cookies = request.COOKIES
    try:
        username = json.loads(cookies.get("username"))
        usertype = json.loads(cookies.get("usertype"))
        age = json.loads(cookies.get("age"))
        password = json.loads(cookies.get("password"))
    except TypeError:
        # 未登录，跳转到登录界面
        return redirect('/login')
    if request.method == "POST" and request.POST:
        # 获取用户通过POST提交过来的数据
        new_usm = request.POST.get('new_usm')
        new_pwd = request.POST.get('new_pwd')
        new_age = request.POST.get('new_age')
        bio = request.POST.get('bio')
        user = Users.objects.get(用户名=username)
        try:
            user.用户名 = new_usm
            user.密码 = new_pwd
            user.年龄 = int(new_age)
            user.save()
            return render(request, 'profile.html',
                          {'username': new_usm, 'usertype': usertype, 'age': new_age, 'password': new_pwd, 'bio': bio})
        except:
            messages.error(request, "修改失败！请检查输入。")
    return render(request, 'profile.html',
                  {'username': username, 'usertype': usertype, 'age': age, 'password': password, 'bio': bio})
