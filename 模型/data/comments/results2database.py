import json
import datetime
import pyodbc
import random
import pickle as pkl

import sys

sys.path.append("../../")
from database.SQL import Sql

cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=LAPTOP-38ACSOA2;DATABASE=情感分析系统;UID=sa;PWD=')

with open("result.json", encoding="utf-8") as f:
    for idx, line in enumerate(f.readlines()):
        result = json.loads(line)
        comment_id = int(result["comment_id"])
        aspects = ";".join(
            [item["aspect"] + "-" + ",".join(item["opinions"]) + "-" + item["sentiment_polarity"] for item in
             result["ap_list"]])
        sql = "INSERT INTO 结论数据表 VALUES({0}, {1}, '{2}', '{3}');".format(idx + 1, comment_id, aspects, "2022-4-27")
        Sql(cnxn, sql, isSelect=False)
