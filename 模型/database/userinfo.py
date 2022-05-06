import pyodbc
import random
import datetime
from SQL import Sql

cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=LAPTOP-38ACSOA2;DATABASE=情感分析系统;UID=sa;PWD=')


def userinfo_init():
    with open("常用中文名.txt", "r", encoding="utf-8") as f:
        names = [line.strip() for line in f.readlines()]
        f.close()
        
    year = str(random.randint(2020, 2021))
    month = str(random.randint(1, 12))
    day = str(random.randint(1, 28))
    date = year + "-" + month + "-" + day
    sampled_names = random.sample(names, 5672)
    bio = "这个人很懒，没有留下任何信息"
    for idx, name in enumerate(sampled_names):
        age = random.randint(18, 75)
        sql = "INSERT INTO 用户信息表 VALUES({0}, '{1}', '12345', {2}, '顾客', '{3}', '{4}');".format(idx + 1, name, age, date, bio)
        Sql(cnxn, sql, isSelect=False)


def get_ID():
    sql = "SELECT ID FROM 用户信息表;"
    IDs = Sql(cnxn, sql, isSelect=True)
    for i, id in enumerate(IDs):
        if id[0] == (i + 1):
            continue
        else:
            return i + 1
    return len(IDs) + 1


def userinfo_register(username, password, age, identity):
    # 新用户注册，注册信息包括注册用户名、密码、年龄
    if username == "":
        string = "用户名不能为空！"
        return string
    elif age == "":
        string = "年龄不能为空！"
        return string
    try:
        age = int(age)
    except:
        string = "注册失败！请检查年龄是否输入正确"
        return string
    idx = get_ID()
    date = datetime.datetime.now()
    bio = "这个人很懒，没有留下任何信息"
    sql = "INSERT INTO 用户信息表 VALUES({0}, '{1}', '{2}', {3}, '{4}', '{5}', '{6}');".format(idx, username, password, age, identity, date, bio)
    Sql(cnxn, sql, isSelect=False)
    string = "注册成功！用户名为：{0}，密码为：{1}".format(username, password)
    return string


def userinfo_login(username, password):
    # 用户登录
    if username == "":
        string = "用户名不能为空！"
        return string
    sql = "SELECT 密码 FROM 用户信息表 WHERE 用户名='{0}';".format(username)
    try:
        result = Sql(cnxn, sql, isSelect=True)
    except pyodbc.ProgrammingError:
        # 用户名不存在
        string = "用户名不存在！"
        return string
    if result[0][0] == password:
        string = "登录成功！"
        # TODO: 登录成功
    else:
        string = "登录失败！密码错误！"
    return string


if __name__ == "__main__":
    userinfo_init()
    #print(userinfo_login("刘臻劼", "1234"))
