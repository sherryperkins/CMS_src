#encoding:utf-8
from exts import db
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
class Members(db.Model):
    __tablename__ = 'jq_member'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)  # 用户名不能为空,而且必须是唯一的
    _password = db.Column(db.String(100), nullable=False)  # 密码不能为空
    email = db.Column(db.String(50), nullable=False, unique=True)  # 用户邮箱不能为空，而且必须是唯一的
    vatar=db.Column(db.String(80),nullable=True)#用户头像
    nickname=db.Column(db.String(50),nullable=True)#用户昵称
    sex = db.Column(db.String(2), default=0)  # 性别
    telephone = db.Column(db.String(11))  # 电话
    status = db.Column(db.Integer)  # 状态
    def __init__(self,username,password,email):
         self.username=username
         self.password=password
         self.email=email
    #获取密码
    @property
    def password(self):
         return self._password
    #设置密码
    @password.setter
    def password(self,raw_password):
         self._password=generate_password_hash(raw_password)#密码加密
    #检查密码
    def check_password(self,raw_password):
         result=check_password_hash(self.password,raw_password)#
         return result