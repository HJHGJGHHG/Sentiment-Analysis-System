import pyodbc
import random
import pickle as pkl

import sys

sys.path.append("../")
from database.SQL import Sql

cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=LAPTOP-38ACSOA2;DATABASE=情感分析系统;UID=sa;PWD=')


def car_comment_init():
    with open("../data/comments/car.txt", "r", encoding="utf-8") as f:
        car_comments = [line.strip() for line in f.readlines()]
        f.close()

    for idx, car_comment in enumerate(car_comments):
        customer_id = random.randint(0, 30000)
        year = str(random.randint(2018, 2021))
        month = str(random.randint(1, 12))
        day = str(random.randint(1, 28))
        date = year + "-" + month + "-" + day
        sql = "INSERT INTO 评论数据表 VALUES({0}, {1}, 0, '{2}', '{3}');".format(idx + 1, customer_id, date, car_comment)
        try:
            Sql(cnxn, sql, isSelect=False)
        except:
            print(sql)
            continue

def tea_comment_init():
    with open("../data/comments/tea.txt", "r", encoding="utf-8") as f:
        tea_comments = [line.strip() for line in f.readlines()]
        f.close()

    for idx, tea_comment in enumerate(tea_comments):
        customer_id = random.randint(10000, 40000)
        year = str(random.randint(2018, 2021))
        month = str(random.randint(1, 12))
        day = str(random.randint(1, 28))
        date = year + "-" + month + "-" + day
        sql = "INSERT INTO 评论数据表 VALUES({0}, {1}, 1, '{2}', '{3}');".format(idx + 24138, customer_id, date, tea_comment)
        try:
            Sql(cnxn, sql, isSelect=False)
        except:
            print(sql)
            continue

def beaf_comment_init():
    with open("../data/comments/beaf.txt", "r", encoding="utf-8") as f:
        beaf_comments = [line.strip() for line in f.readlines()]
        f.close()

    for idx, beaf_comment in enumerate(beaf_comments):
        customer_id = random.randint(40000, 45000)
        year = str(random.randint(2018, 2021))
        month = str(random.randint(1, 12))
        day = str(random.randint(1, 28))
        date = year + "-" + month + "-" + day
        sql = "INSERT INTO 评论数据表 VALUES({0}, {1}, 2, '{2}', '{3}');".format(idx + 27713, customer_id, date, beaf_comment)
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
    beaf_comment_init()
