#encoding:utf-8
from exts import db
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
class Members(db.Model):
    __tablename__ = 'jq_member'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)  # �û�������Ϊ��,���ұ�����Ψһ��
    _password = db.Column(db.String(100), nullable=False)  # ���벻��Ϊ��
    email = db.Column(db.String(50), nullable=False, unique=True)  # �û����䲻��Ϊ�գ����ұ�����Ψһ��
    vatar=db.Column(db.String(80),nullable=True)#�û�ͷ��
    nickname=db.Column(db.String(50),nullable=True)#�û��ǳ�
    sex = db.Column(db.String(2), default=0)  # �Ա�
    telephone = db.Column(db.String(11))  # �绰
    status = db.Column(db.Integer)  # ״̬
    def __init__(self,username,password,email):
         self.username=username
         self.password=password
         self.email=email
    #��ȡ����
    @property
    def password(self):
         return self._password
    #��������
    @password.setter
    def password(self,raw_password):
         self._password=generate_password_hash(raw_password)#�������
    #�������
    def check_password(self,raw_password):
         result=check_password_hash(self.password,raw_password)#
         return result