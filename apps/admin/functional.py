# -*- coding:utf-8 -*-
from flask import session
from .models import Users,Role,Auth
from exts import db
import config
def get_auths(parent_id):
    user_id = session.get(config.ADMIN_USER_ID)
    admin = Users.query.join(
        Role
    ).filter(
        Role.id == Users.role_id,
        Users.uid == user_id
    ).first()
    auths = admin.jq_role.auths  # 将原本存储的权限字符串转换为列表
    auths_list1 = auths.split(",")
    auths_list2 = []
    for i, val in enumerate(auths_list1):
        auths_list2.append(int(val))
    auths_list3 = []
    authszz = []
    auth_list = Auth.query.all()
    for i in auth_list:
        for v in auths_list2:
            if v == i.id:
                auths_list3.append(i.url)
    # 开始取得内容管理下的所有权限
    content_auths = db.session.query(Auth).filter(Auth.parent_id ==parent_id).all()
    for i in content_auths:
        for v in auths_list3:
            if v == i.url:
                authszz.append(i)
    return authszz#返回有权返回的对象
#测试根菜单是否有权限
def test_auths(id):
    user_id = session.get(config.ADMIN_USER_ID)
    admin = Users.query.join(
        Role
    ).filter(
        Role.id == Users.role_id,
        Users.uid == user_id
    ).first()
    auths = admin.jq_role.auths  # 将原本存储的权限字符串转换为列表
    auths_list1 = auths.split(",")
    auths_list2 = []
    for i, val in enumerate(auths_list1):
        auths_list2.append(int(val))
    auths_list3 = []
    authszz = []
    auth_list = Auth.query.all()
    for i in auth_list:
        for v in auths_list2:
            if v == i.id:
                auths_list3.append(i.url)
    # 指定根菜单是否有访问权限
    content_auths = db.session.query(Auth).filter(Auth.id ==id).first()
    for v in auths_list3:
            if v == content_auths.url:
                authszz.append(i)
    if authszz:
        result=1
    else:
        result = 1
    return result#返回有权返回的对象