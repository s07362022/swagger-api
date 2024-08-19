import mysql.connector

# MySQL 連接設置
db_config = {
    'user': 'root',
    'password': '0000',
    'host': 'localhost',
    'database': 'harden_web_micor'
}

cnx = mysql.connector.connect(**db_config)
cursor = cnx.cursor()

# cursor.execute("Show tables;")

# 讀取類別資料
import pandas as pd
def get_classes():
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    cursor.execute("SELECT name, folder FROM classes")
    result = cursor.fetchall()
    # q = "SELECT name, folder FROM classes"
    # df = pd.read_sql(q,cnx)
    # print(df)
    # print(df.head(5))
    cnx.close()
    # for name, folder in result:
        # print(name)
    return {name: folder for name, folder in result}



# 讀取文件資料
def get_files():
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    cursor.execute("SELECT name, path FROM files")
    result = cursor.fetchall()
    cnx.close()
    return {name: path for name, path in result}

get_classes()
# print(c)