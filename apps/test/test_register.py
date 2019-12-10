# -*- coding:utf-8 -*-
import unittest#导入unittest模块
import json#导入json模块
import sys#导入sys模块
sys.path.append('../../')#设定app.py文件所在路径，实际是根目录
from app import create_app#导入create_app模块
from flask import json#导入json
app=create_app()#app初始化
class TestLogin(unittest.TestCase):#定义TestLogin类，测试用户登录功能
    def print_into(self, a):#清除残余测试数据提示
        print("clearing...")
    def setUp(self):
        app.testing = True  # 指定app在测试模式下运行，让其抛出异常
        # Flask客户端可以模拟发送诸如GET和POST请求
        self.client = app.test_client()
        print("测试用户登录开始，使用错误的用户名或密码")
    def tearDown(self):
        print("测试用户登录结束，可以清除相应的测试数据")
        self.addCleanup(self.print_into,"clearing...")#清除残余数据
    def test_error_username_password(self):
        #测试错误的用户名或密码,服务器发出的JSON格式数据放入response
        response =app.test_client().post('/login?url=/', data = {"username": "zhangsan1", "password": "100258"})#模拟用户发出POST请求
        # 使用respoonse.data取得服务器响应数据
        resp_json = response.data
        # 以json格式解析数据
        resp_dict = json.loads(resp_json)
        # 使用断言，验证resp_dict是否包含code子串，若code不是resp_dist的子串，返回Flase
        self.assertIn("code", resp_dict)
        # 使用get获取resp_dict中的code
        code = resp_dict.get("code")
        #使用断言验证，验证code的值是否为2，不为2的话，返回结果为Flase,否则返回OK.
        self.assertEqual(code, 2)



