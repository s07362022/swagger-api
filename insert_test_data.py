import mysql.connector

# MySQL 連接設置
db_config = {
    'user': 'root',
    'password': '0000',
    'host': 'localhost',
    'database': 'harden_web_micor'
} #dict

# 測試數據 list 
# () tuple
users_data = [
    ('user1', 'password1', 'key1'),
    ('user2', 'password2', 'key2')
]

files_data = [
    ('肝臟模型', 'liver_model.txt'),
    ('乳癌ki67模型', 'breast_cancer_ki67_model.txt'),
    ('肝纖維模型', 'liver_fibrosis_model.txt'),
    ('油滴模型', 'oil_drop_model.txt')
]

classes_data = [
    ('肝臟影像1', 'liver_images1'),
    ('乳癌ki67影像1', 'breast_cancer_ki67_images1'),
    ('肝纖維影像1', 'liver_fibrosis_images1'),
    ('油滴影像1', 'oil_drop_images1')
]

# 連接到 MySQL 資料庫
cnx = mysql.connector.connect(**db_config)
cursor = cnx.cursor()

cursor.execute("Show tables;")
 
myresult = cursor.fetchall()
 
for x in myresult:
    print(x)


# 插入 users 測試數據 
# cursor.executemany("INSERT INTO users (username, password, `key`) VALUES (%s, %s, %s)", users_data)

# 插入 files 測試數據
# cursor.executemany("INSERT INTO files (name, path) VALUES (%s, %s)", files_data)

# 插入 classes 測試數據
cursor.executemany("INSERT INTO classes (name, folder) VALUES (%s, %s)", classes_data)

# 提交變更
cnx.commit()

# 關閉連接
cursor.close()
cnx.close()

print("測試數據已插入")
