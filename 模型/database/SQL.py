import pyodbc


def Sql(cnxn, sql, isSelect):
    """
    执行一条SQL语句
    :param cnxn:
    :param sql: SQL语句
    :param isSelect: 是否为查询语句
    :return: 若为查询语句，返回结果
    """
    cursor = cnxn.cursor()
    cursor.execute(str(sql))
    if isSelect:
        ans = cursor.fetchall()
    cursor.commit()
    cursor.close()
    if isSelect:
        return ans
