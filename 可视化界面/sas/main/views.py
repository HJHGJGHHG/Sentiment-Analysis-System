import json
from django.contrib import messages
from django.shortcuts import render, redirect

import sys

sys.path.append("../")
from Login.models import Users
from main.models import Comments


# Create your views here.
def main(request):
    cookies = request.COOKIES
    try:
        username = json.loads(cookies.get("username"))
        usertype = json.loads(cookies.get("usertype"))
    except TypeError:
        # 未登录，跳转到登录界面
        return redirect('/login')
    if usertype == "顾客":
        return render(request, 'index_customer.html', {'username': username, 'usertype': usertype})
    else:
        return render(request, 'index_manager.html', {'username': username, 'usertype': usertype})


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
    if usertype == "顾客":
        return profile_customer(request, username, usertype, age, password, bio)
    else:
        return profilt_manager(request, username, usertype, age, password, bio)


def profile_customer(request, username, usertype, age, password, bio):
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
            return render(request, 'profile_customer.html',
                          {'username': new_usm, 'usertype': usertype, 'age': new_age, 'password': new_pwd,
                           'bio': bio})
        except:
            # TODO: 添加修改失败信息
            # messages.error(request, "修改失败！请检查输入。")
            pass
    return render(request, 'profile_customer.html',
                  {'username': username, 'usertype': usertype, 'age': age, 'password': password, 'bio': bio})


def profilt_manager(request, username, usertype, age, password, bio, customer_ID=1):
    customer_info = Users.objects.get(ID=customer_ID)
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
            return render(request, 'profile_manager.html',
                          {'username': new_usm, 'usertype': usertype, 'age': new_age, 'password': new_pwd,
                           'bio': bio, 'customer_ID': customer_info.ID, 'customer_username': customer_info.用户名,
                           'customer_age': customer_info.年龄, 'customer_password': customer_info.密码
                           })
        except:
            # TODO: 添加修改失败信息
            # messages.error(request, "修改失败！请检查输入。")
            pass
    if request.method == "GET":
        # 新建查询
        customer_IDorUsername = request.GET.get('customer_info')
        if customer_IDorUsername is None:
            pass
        else:
            try:
                customer_info = Users.objects.get(ID=customer_IDorUsername)
            except:
                try:
                    customer_info = Users.objects.get(用户名=customer_IDorUsername)
                except:
                    return render(request, 'profile_manager.html',
                                  {'username': username, 'usertype': usertype, 'age': age, 'password': password,
                                   'bio': bio, 'customer_ID': customer_info.ID, 'customer_username': customer_info.用户名,
                                   'customer_age': customer_info.年龄, 'customer_password': customer_info.密码,
                                   'content1': '查询失败！请检查输入是否正确。',
                                   })
    return render(request, 'profile_manager.html',
                  {'username': username, 'usertype': usertype, 'age': age, 'password': password,
                   'bio': bio, 'customer_ID': customer_info.ID, 'customer_username': customer_info.用户名,
                   'customer_age': customer_info.年龄, 'customer_password': customer_info.密码
                   })


def comments(request):
    cookies = request.COOKIES
    try:
        username = json.loads(cookies.get("username"))
        usertype = json.loads(cookies.get("usertype"))
        age = json.loads(cookies.get("age"))
        password = json.loads(cookies.get("password"))
        ID = json.loads(cookies.get("ID"))
        comments = Comments.objects.filter(顾客id=7979)
        for item in comments:
            print(item.评论内容)
    except TypeError:
        # 未登录，跳转到登录界面
        return redirect('/login')
    if usertype == "顾客":
        return comments_customer(request, username, usertype, age, password)
    else:
        # return profilt_manager(request, username, usertype, age, password, bio)
        pass


def comments_customer(request, username, usertype, age, password):
    if request.method == "POST" and request.POST:
        # 获取用户通过POST提交过来的数据
        product_ID = request.POST.get('product_ID')
        date = request.POST.get('date')
        comment_text = request.POST.get('comment_text')
        print(product_ID)
        print(date)
        print(comment_text)
    return render(request, 'comments_customer.html',
                  {'username': username, 'usertype': usertype, 'age': age, 'password': password})
