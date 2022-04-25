import json
import pyodbc

import sys

sys.path.append("../")
from database.SQL import Sql

cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=LAPTOP-38ACSOA2;DATABASE=情感分析系统;UID=sa;PWD=')


def get_result_id():
    sql = "SELECT 结论ID FROM 结论数据表;"
    IDs = Sql(cnxn, sql, isSelect=True)
    for i, id in enumerate(IDs):
        if id[0] == (i + 1):
            continue
        else:
            return i + 1
    return len(IDs) + 1


def store_results():
    file = open("../data/comments/result.json", "r", encoding="utf-8")
    result_id = get_result_id()
    for idx, line in enumerate(file.readlines()):
        result = json.loads(line)
        aspect = ";".join(
            [item["aspect"] + "-" + ','.join(item["opinions"]) + "-" + item["sentiment_polarity"] for item in
             result["ap_list"]]).replace("'", "")
        sql = "INSERT INTO 结论数据表 VALUES ({0}, {1}, '{2}');".format(
            result_id + idx,
            int(result["comment_id"]),
            aspect
        )
        try:
            Sql(cnxn, sql, isSelect=False)
        except:
            print(sql)
            break


if __name__ == "__main__":
    store_results()
