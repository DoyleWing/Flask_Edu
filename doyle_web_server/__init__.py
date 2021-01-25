import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app=Flask(__name__)

app.config["SECRET_KEY"]="XXXXXXX"
app.config["SQLALCHEMY_DATABASE_URI"] = 'XXXXX'  #数据库

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_message_category = 'info'
login_manager.login_message = u"这不是你该接触到的"  #汉化处理
login_manager.login_view = 'login'

app.config['MAIL_SERVER'] = 'smtp.163.com'
# 163:Non SSL: 25 SSL:465/994
app.config['MAIL_PORT'] = 553
app.config['MAIL_USE_SSL'] = True   #开启安全检测
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')   #获取环境变量
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')

mail = Mail(app)

from doyle_web_server import routes
