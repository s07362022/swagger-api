from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
import os
import json
import mysql.connector
import datetime
from cryptography.fernet import Fernet

#Gmail#################################
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
import smtplib
def smtp(label):
    content = MIMEMultipart()  #建立MIMEMultipart物件
    content["subject"] = "顯微鏡平台回饋建議"  #郵件標題
    content["from"] = "gish1040403@gmail.com"  #寄件者
    content["to"] = "s10059011@gm2.nutn.edu.tw" #收件者
    timenow = datetime.datetime.now()
    timenow = str(timenow)
    content.attach(MIMEText(timenow + " " +label))  #郵件內容
    # phto = Path(img_name).read_bytes()
    # content.attach(MIMEImage(phto))
    #文字
    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login("gish1040403@gmail.com", "cffakphyrorydcti")  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("Complete!")
        except Exception as e:
            print("Error message: ", e)
#######################################

app = Flask(__name__)
app.secret_key = 'Q36111223'  # 為了顯示flash訊息，需要設置一個密鑰

# MySQL 連接設置
db_config = {
    'user': 'root',
    'password': '0000',
    'host': 'localhost',
    'database': 'harden_web_micor'
}

# 檢查文件是否允許上傳
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 讀取類別資料
def get_classes():
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    cursor.execute("SELECT name, folder FROM classes")
    result = cursor.fetchall()
    cnx.close()
    return {name: folder for name, folder in result}

# 讀取文件資料
def get_files():
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    cursor.execute("SELECT name, path FROM files")
    result = cursor.fetchall()
    cnx.close()
    return {name: path for name, path in result}

# 登錄頁面
@app.route('/')
def home():
    return render_template('login.html')

# 處理登錄請求
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()

    if user:
        session['username'] = username
        session['logged_in'] = True

        # 檢查是否已經輸入過 SerialNumber
        cursor.execute("SELECT * FROM user_serials WHERE username=%s", (username,))
        user_serial = cursor.fetchone()

        if user_serial:
            cnx.close()
            flash('登入成功')
            return redirect(url_for('main'))
        else:
            cnx.close()
            flash('首次登入，請輸入主機板資訊')
            return redirect(url_for('enter_serial'))
    else:
        cnx.close()
        flash('帳號或密碼錯誤')
        return redirect(url_for('home'))

# 輸入主機板資訊頁面
@app.route('/enter_serial')
def enter_serial():
    if 'username' not in session:
        flash('請先登入')
        return redirect(url_for('home'))
    return render_template('enter_serial.html')

# 處理主機板資訊提交
@app.route('/submit_serial', methods=['POST'])
def submit_serial():
    if 'username' not in session:
        flash('請先登入')
        return redirect(url_for('home'))

    serial_number = request.form['serial_number']
    # 生成新的加密金鑰
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    encrypted_serial = cipher_suite.encrypt(serial_number.encode()).decode()

    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    cursor.execute("INSERT INTO user_serials (username, serial_number, encrypted_serial) VALUES (%s, %s, %s)",
                   (session['username'], serial_number, encrypted_serial))
    cnx.commit()
    cnx.close()

    # 將金鑰顯示給使用者並提示保存
    return render_template('show_key.html', key=key.decode())

# 功能選擇頁面
@app.route('/main')
def main():
    if 'username' not in session:
        flash('請先登入')
        return redirect(url_for('home'))
    return render_template('main.html', username=session['username'])

# 下載頁面
@app.route('/download')
def download():
    if 'username' not in session:
        flash('請先登入')
        return redirect(url_for('home'))
    files = get_files()
    return render_template('download.html', files=files, username=session['username'])

# 處理文件下載請求
@app.route('/download_file')
def download_file():
    if 'username' not in session:
        flash('請先登入')
        return redirect(url_for('home'))
    filename = request.args.get('filename')
    if not filename:
        flash('未選擇文件')
        return redirect(url_for('download'))
    files = get_files()
    if filename in files:
        file_path = os.path.join('./static', 'model', files[filename])
        log_download(session['username'], filename)
        return send_file(file_path, as_attachment=True)
    else:
        flash('文件不存在')
        return redirect(url_for('download'))

# 上傳頁面
@app.route('/upload')
def upload():
    if 'username' not in session:
        flash('請先登入')
        return redirect(url_for('home'))
    classes = get_classes()
    return render_template('upload.html', classes=classes, username=session['username'])

# 處理文件上傳請求
@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'username' not in session:
        flash('請先登入')
        return redirect(url_for('home'))
    if 'files' not in request.files or 'class' not in request.form:
        flash('沒有選擇文件或類別')
        return redirect(url_for('upload'))
    files = request.files.getlist('files')
    selected_class = request.form['class']
    if not files or files[0].filename == '':
        flash('沒有選擇文件')
        return redirect(url_for('上傳'))
    classes = get_classes()
    if selected_class not in  classes:
        flash('選擇的類別無效')
        return redirect(url_for('上傳'))
    upload_folder = os.path.join(app.root_path, 'uploads', session['username'], classes[selected_class])
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    saved_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            saved_files.append(filename)
    if saved_files:
        flash(f'文件上傳成功，共上傳 {len(saved_files)} 個文件')
        log_upload(session['username'], selected_class, saved_files)
        return redirect(url_for('上傳'))
    else:
        flash('文件上傳失敗，僅允許上傳影像文件')
        return redirect(url_for('上傳'))

# 下載記錄頁面
@app.route('/download_log')
def download_log():
    if 'username' not in session:
        flash('請先登入')
        return redirect(url_for('home'))
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM download_logs")
    logs = cursor.fetchall()
    cnx.close()
    return render_template('download_log.html', logs=logs, username=session['username'])

# 建議與回饋頁面
@app.route('/feedback')
def feedback():
    if 'username' not in session:
        flash('請先登入')
        return redirect(url_for('home'))
    return render_template('feedback.html', username=session['username'])

# 處理建議與回饋提交
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'username' not in session:
        flash('請先登入')
        return redirect(url_for('home'))

    feedback_content = request.form['feedback']

    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    cursor.execute("INSERT INTO feedback (username, feedback, timestamp) VALUES (%s, %s, %s)",
                   (session['username'], feedback_content, datetime.datetime.now()))
    cnx.commit()
    cnx.close()

    flash('感謝您的建議與回饋！')
    label = "來自{}的意見回覆".format(session['username'])
    smtp(label)
    return redirect(url_for('home'))

# 記錄下載日志
def log_download(username, filename):
    log_entry = {
        "username": username,
        "filename": filename,
        "timestamp": datetime.now().isoformat()
    }
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    cursor.execute("INSERT INTO download_logs (username, filename, timestamp) VALUES (%s, %s, %s)",
                   (username, filename, log_entry['timestamp']))
    cnx.commit()
    cnx.close()

# 記錄上傳日志
def log_upload(username, selected_class, filenames):
    log_entry = {
        "username": username,
        "class": selected_class,
        "file_count": len(filenames),
        "filenames": json.dumps(filenames),
        "timestamp": datetime.now().isoformat()
    }
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    cursor.execute("INSERT INTO upload_logs (username, class, file_count, filenames, timestamp) VALUES (%s, %s, %s, %s, %s)",
                   (username, selected_class, log_entry['file_count'], log_entry['filenames'], log_entry['timestamp']))
    cnx.commit()
    cnx.close()

# 登出
@app.route('/logout')
def logout():
    session.clear()
    flash('您已登出')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2022,debug=True)
