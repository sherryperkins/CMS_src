# -*- coding:utf-8 -*-
import unittest#导入unittest模块
import sys#导入json模块
sys.path.append('../../')#设定app.py文件所在路径，实际是根目录
from app import create_app#导入create_app模块
app = create_app()#app初始化
class JiaQiTest(unittest.TestCase):#定义JiaQiTest类
    def print_into(self, a):#清除残余测试数据提示
        print("clearing...")
    def setUp(self):#定义setUp()方法，进行初始化
        self.app=app.test_client()#Flask客户端可以模拟发送诸如GET和POST请求
        print("set up")
    def tearDown(self):#定义tearDown()方法，进行测试结束收尾工作
        print("down")
        self.addCleanup(self.print_into, "clearing...")  # 清除残余数据
    def test_index(self):#定义test_index()方法，就是测试用例的实例
        pass
