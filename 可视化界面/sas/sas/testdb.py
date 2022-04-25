from django.http import HttpResponse

import sys

sys.path.append("../")
from Login.models import Users


# 数据库操作
def testdb(request):
    # 初始化
    response = ""
    
    # 通过objects这个模型管理器的all()获得所有数据行，相当于SQL中的SELECT * FROM
    list = Users.objects.all()
    # 输出所有数据
    for var in list:
        response += var.用户名 + " "
    return HttpResponse("<p>" + response + "</p>")
