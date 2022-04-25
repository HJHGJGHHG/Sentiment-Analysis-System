import pyodbc
import random
import pickle as pkl

import sys

sys.path.append("../")
from database.SQL import Sql

cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=LAPTOP-38ACSOA2;DATABASE=情感分析系统;UID=sa;PWD=')


def get_comment_id():
    sql = "SELECT 评论ID FROM 评论数据表;"
    IDs = Sql(cnxn, sql, isSelect=True)
    for i, id in enumerate(IDs):
        if id[0] == (i + 1):
            continue
        else:
            return i + 1
    return len(IDs) + 1


def car_comment_init():
    with open("../data/comments/car.txt", "r", encoding="utf-8") as f:
        car_comments = [line.strip() for line in f.readlines()]
        f.close()
    
    comment_id = get_comment_id()
    for idx, car_comment in enumerate(car_comments):
        customer_id = random.randint(0, 30000)
        year = str(random.randint(2018, 2021))
        month = str(random.randint(1, 12))
        day = str(random.randint(1, 28))
        date = year + "-" + month + "-" + day
        sql = "INSERT INTO 评论数据表 VALUES({0}, {1}, 0, '{2}', '{3}');".format(idx + comment_id, customer_id, date,
                                                                            car_comment.strip())
        try:
            Sql(cnxn, sql, isSelect=False)
        except:
            print(sql)
            continue


def tea_comment_init():
    with open("../data/comments/tea.txt", "r", encoding="utf-8") as f:
        tea_comments = [line.strip() for line in f.readlines()]
        f.close()
    
    comment_id = get_comment_id()
    for idx, tea_comment in enumerate(tea_comments):
        customer_id = random.randint(10000, 40000)
        year = str(random.randint(2018, 2021))
        month = str(random.randint(1, 12))
        day = str(random.randint(1, 28))
        date = year + "-" + month + "-" + day
        sql = "INSERT INTO 评论数据表 VALUES({0}, {1}, 1, '{2}', '{3}');".format(idx + comment_id, customer_id, date,
                                                                            tea_comment.strip())
        try:
            Sql(cnxn, sql, isSelect=False)
        except:
            print(sql)
            continue


def beaf_comment_init():
    with open("../data/comments/beaf.txt", "r", encoding="utf-8") as f:
        beaf_comments = [line.strip() for line in f.readlines()]
        f.close()
    
    comment_id = get_comment_id()
    for idx, beaf_comment in enumerate(beaf_comments):
        customer_id = random.randint(40000, 45000)
        year = str(random.randint(2018, 2021))
        month = str(random.randint(1, 12))
        day = str(random.randint(1, 28))
        date = year + "-" + month + "-" + day
        sql = "INSERT INTO 评论数据表 VALUES({0}, {1}, 2, '{2}', '{3}');".format(idx + comment_id, customer_id, date,
                                                                            beaf_comment.strip())
        try:
            Sql(cnxn, sql, isSelect=False)
        except:
            print(sql)
            continue


def load_all_comment():
    # 从数据库中取出所有评论用以模型分析
    sql = "SELECT 评论ID, 评论内容 FROM 评论数据表"
    result = {"id": [], "text": []}
    for item in Sql(cnxn, sql, isSelect=True):
        result["id"].append(int(item[0]))
        result["text"].append(str(item[1]))
    return result


if __name__ == "__main__":
    car_comment_init()
    tea_comment_init()
    beaf_comment_init()
