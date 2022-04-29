import os
import json
import datetime
import subprocess
import pickle as pkl
from django.shortcuts import render, redirect
from django.http import QueryDict, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import sys

sys.path.append("../")
from collections import Counter
from Login.models import Users
from django.db.models import Max
from main.models import Comments, Results
from main.predict import predict


def cmd_deal(cmd: str):
    xe = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    while True:
        rt_data = xe.stdout.readline().decode("GBK")
        if rt_data != "":
            print(rt_data, end="")
        else:
            break
    return xe.wait()  # 执行成功返回0，执行失败返回1


def get_comment_ID():
    IDs = [id.评论id for id in Comments.objects.all()]
    for i, id in enumerate(IDs):
        if id == (i + 1):
            continue
        else:
            return i + 1
    return len(IDs) + 1


def get_result_ID():
    IDs = [id.结论id for id in Results.objects.all()]
    for i, id in enumerate(IDs):
        if id == (i + 1):
            continue
        else:
            return i + 1
    return len(IDs) + 1


def get_items():
    # 获取 “顾客与评论分析” 上方四个 box 部分中的数据
    customers_num = Users.objects.count()
    comments_num = Comments.objects.count()
    lastmonth = datetime.datetime.now() - datetime.timedelta(days=30)
    new_comments = Comments.objects.filter(评论时间__gte=lastmonth)
    active_users = Users.objects.filter(ID__in=[ids.顾客id.ID for ids in new_comments]).count()
    return customers_num, comments_num, new_comments.count(), active_users


def get_index():
    # 获得表格 x 轴属性
    month = datetime.datetime.today().month
    if month in [1, 3, 5, 7, 8, 10, 12]:
        days = 31
    elif month == 2:
        if datetime.datetime.today().year % 4 == 0:
            days = 29
        else:
            days = 28
    else:
        days = 30
    return list(range(1, days + 1))


def get_newCustomers():
    # 获得新增用户数据
    lastmonth = datetime.datetime.today() - datetime.timedelta(days=datetime.datetime.today().day)
    new_customers = [item.注册时间.day - 1 for item in Users.objects.filter(注册时间__gte=lastmonth)]
    index = get_index()
    data = [0] * len(index)
    for day in new_customers:
        data[day] += 1
    return data, index


def get_newComments():
    # 获得新增评论数据
    lastmonth = datetime.datetime.today() - datetime.timedelta(days=datetime.datetime.today().day)
    new_customers = [item.评论时间.day - 1 for item in Comments.objects.filter(评论时间__gte=lastmonth)]
    index = get_index()
    data = [0] * len(index)
    for day in new_customers:
        data[day] += 1
    return data


def parse_aspect(aspect):
    # 处理属性极性对
    result = ""
    aspects = aspect.split(";")
    for item in aspects:
        result += "".join(item.split("-")[:2])
        result += " "
    return result


def concate_aspect_and_opinion(text, aspect, opinions):
    aspect_text = ""
    for opinion in opinions:
        if text.find(aspect) <= text.find(opinion):
            aspect_text += aspect + opinion + "，"
        else:
            aspect_text += opinion + aspect + "，"
    aspect_text = aspect_text[:-1]
    
    return list(aspect_text.split("，"))


def add_results():
    with open("D:/Desktop/Sentiment-Analysis-System/可视化界面/sas/result.json", "rb") as f:
        for line in f.readlines():
            result = json.loads(line)
            comment_id = int(result["comment_id"])
            aspects = ";".join(
                [item["aspect"] + "-" + ",".join(item["opinions"]) + "-" + item["sentiment_polarity"] for item in
                 result["ap_list"]])
            date = datetime.datetime.now()
            Results.objects.create(结论id=get_result_ID(), 评论id=Comments.objects.get(评论id=comment_id), 属性极性对=aspects,
                                   更新时间=date)


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
        return profile(request)
    else:
        data = get_items()
        if request.method == "POST":
            new_customer, index = get_newCustomers()
            new_comment = get_newComments()
            return JsonResponse({"index": index, "new_customer": new_customer, "new_comment": new_comment})
        return render(request, 'index.html',
                      {'username': username, 'usertype': usertype,
                       'customers_num': data[0], 'comments_num': data[1],
                       'new_comments': data[2], 'active_users': data[3]
                       })


def profile(request):
    cookies = request.COOKIES
    try:
        username = json.loads(cookies.get("username"))
        usertype = json.loads(cookies.get("usertype"))
        age = json.loads(cookies.get("age"))
        password = json.loads(cookies.get("password"))
        bio = Users.objects.get(用户名=username).个人简介
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
            user.个人简介 = bio
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
            user.个人简介 = bio
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
                                   'content1': '查询失败！请检查输入是否正确。', 'customer_bio': customer_info.个人简介
                                   })
    return render(request, 'profile_manager.html',
                  {'username': username, 'usertype': usertype, 'age': age, 'password': password,
                   'bio': bio, 'customer_ID': customer_info.ID, 'customer_username': customer_info.用户名,
                   'customer_age': customer_info.年龄, 'customer_password': customer_info.密码,
                   'customer_bio': customer_info.个人简介
                   })


@csrf_exempt
def comments(request):
    cookies = request.COOKIES
    try:
        username = json.loads(cookies.get("username"))
        usertype = json.loads(cookies.get("usertype"))
        ID = json.loads(cookies.get("ID"))
    except TypeError:
        # 未登录，跳转到登录界面
        return redirect('/login')
    if usertype == "顾客":
        return comments_customer(request, ID, username, usertype)
    else:
        return comments_manager(request, username, usertype)


def comments_customer(request, ID, username, usertype):
    comments = Comments.objects.filter(顾客id=ID)
    if request.method == "POST" and request.POST:
        # 获取用户通过POST提交过来的数据
        # 添加评论数据
        product_ID = request.POST.get('product_ID')
        date = datetime.datetime.now()
        comment_text = request.POST.get('comment_text')
        # 删除评论数据
        delete_comment_ID = request.POST.get('delete_comment_ID')
        # 修改评论数据
        modify_comment_ID = request.POST.get('modify_comment_ID')
        new_comment_text = request.POST.get('new_comment_text')
        if product_ID is not None and date is not None and comment_text is not None:
            # 添加评论
            try:
                Comments.objects.create(评论id=get_comment_ID(), 顾客id=Users.objects.get(ID=ID), 商品id=int(product_ID),
                                        评论时间=date, 评论内容=comment_text)
                return redirect('/comments')
            except:
                # TODO: 添加增加评论失败提示信息
                print("add fail")
                pass
        if delete_comment_ID is not None:
            # 删除评论
            try:
                Comments.objects.get(评论id=delete_comment_ID, 顾客id=Users.objects.get(ID=ID)).delete()
                return redirect('/comments')
            except:
                # TODO: 添加删除评论失败提示信息
                print("delete fail")
                pass
        if modify_comment_ID is not None and new_comment_text is not None:
            try:
                comment = Comments.objects.get(评论id=modify_comment_ID)
                comment.评论时间 = date
                comment.评论内容 = new_comment_text
                comment.save()
                return redirect('/comments')
            except:
                # TODO: 添加修改评论失败提示信息
                print("modify fail")
                pass
    return render(request, 'comments_customer.html',
                  {'username': username, 'usertype': usertype, 'comments': comments})


def comments_manager(request, username, usertype):
    comments = Comments.objects.all()
    return render(request, 'comments_manager.html',
                  {'username': username, 'usertype': usertype, 'comments': comments})


def opinion(request, id=0):
    cookies = request.COOKIES
    try:
        username = json.loads(cookies.get("username"))
        usertype = json.loads(cookies.get("usertype"))
    except TypeError:
        # 未登录，跳转到登录界面
        return redirect('/login')
    results = Results.objects.filter(评论id__商品id=id)
    results_list, texts, good_rate = opinions_clustering(results)
    # 对新添加评论进行分析
    new_comments = {"id": [], "text": []}
    for item in Comments.objects.filter(评论时间__gt=Results.objects.all().aggregate(Max('更新时间'))["更新时间__max"]):
        new_comments["id"].append(item.评论id)
        new_comments["text"].append(item.评论内容)
    if request.method == "POST" and request.POST:
        if len(new_comments["id"]) != 0:
            pkl.dump(new_comments, open("new_comments.pkl", "wb"))
            predict()
            add_results()
            os.remove("D:/Desktop/Sentiment-Analysis-System/可视化界面/sas/new_comments.pkl")
            os.remove("D:/Desktop/Sentiment-Analysis-System/可视化界面/sas/result.json")
        return render(request, 'opinion.html', {'username': username, 'usertype': usertype, 'results': results_list,
                                                'product_id': id, 'texts': texts, 'good_rate': good_rate,
                                                'new_comments': len(new_comments["id"])
                                                })
    return render(request, 'opinion.html', {'username': username, 'usertype': usertype, 'results': results_list,
                                            'product_id': id, 'texts': texts, 'good_rate': good_rate,
                                            'new_comments': len(new_comments["id"])
                                            })


def opinions_clustering(results):
    aspects_texts_polarities = {}
    results_list = []
    good = 0
    j = 0
    for i, obj in enumerate(results):
        result_tmp = [obj.评论id.评论id, obj.评论id.评论时间, obj.评论id.商品id, obj.评论id.评论内容, ""]
        data = ([item.split("-") for item in obj.属性极性对.split(";")], obj.评论id.评论内容)
        for item in data[0]:
            j += 1
            if item[0] not in aspects_texts_polarities.keys():
                aspects_texts_polarities[item[0]] = [[], []]
            
            opinions = item[1].split(",")
            aspect_texts = concate_aspect_and_opinion(data[1], item[0], opinions)
            result_tmp[4] += " ".join(aspect_texts) + " "
            if item[2] == '正向':
                good += 1
                aspects_texts_polarities[item[0]][0].extend(aspect_texts)
            else:
                aspects_texts_polarities[item[0]][1].extend(aspect_texts)
        results_list.append(result_tmp)
    
    tmp = sorted(aspects_texts_polarities.items(), key=lambda x: len(x[1][0]) + len(x[1][0]), reverse=True)[:20]
    data = [[], []]
    for i in tmp:
        if len(i[1][0]) > len(i[1][1]):
            text = Counter(i[1][0]).most_common(1)[0][0]
            if text[-1] == "不":
                text += "好"
            data[0].append((text, i[0]))
        else:
            text = Counter(i[1][1]).most_common(1)[0][0]
            if text[-1] == "不":
                text += "好"
            data[1].append((text, i[0]))
    return results_list, data, round(good * 100 / j, 2)


def analysis(request, product_id=0, phase=0, aspect=""):
    """
    :param request:
    :param product_id: 商品 id：0,1,2
    :param phase: 0：好评，1：差评
    :param aspect: 属性
    :return:
    """
    cookies = request.COOKIES
    try:
        username = json.loads(cookies.get("username"))
        usertype = json.loads(cookies.get("usertype"))
    except TypeError:
        # 未登录，跳转到登录界面
        return redirect('/login')
    results = Results.objects.filter(评论id__商品id=product_id, 评论id__评论内容__contains=aspect)
    opinions = []
    results_list = [[], []]
    for i, obj in enumerate(results):
        result_tmp = [obj.评论id.评论id, obj.评论id.评论时间, obj.评论id.评论内容, ""]
        data = ([item.split("-") for item in obj.属性极性对.split(";")], obj.评论id.评论内容)
        for item in data[0]:
            if aspect not in item[0]:
                continue
            opinion = item[1].split(",")
            aspect_texts = concate_aspect_and_opinion(data[1], item[0], opinion)
            result_tmp[3] += " ".join(aspect_texts) + " "
            if item[2] == '正向':
                opinions.extend(opinion)
                results_list[0].append(result_tmp)
            else:
                opinions.extend(opinion)
                results_list[1].append(result_tmp)
    
    if request.method == "POST":
        opinions_wordcloud = []
        for item in Counter(opinions).most_common()[:50]:
            opinions_wordcloud.append({"name": item[0], "value": item[1]})
        return JsonResponse({
            "rate": (len(results_list[0]), len(results_list[1])), "opinions_count": opinions_wordcloud})
    return render(request, "analysis.html",
                  {'username': username, 'usertype': usertype, 'product_id': product_id, 'aspect': aspect,
                   "results": results_list, "phase": phase})
