# -*- coding:utf-8 -*-
import unittest#导入unittest模块
import os#导入os模块
class RunCase(unittest.TestCase):
    def test_case(self):#定义test_case测试用例集合函数
        case_path = os.getcwd()  # 测试用例所在路径
        discover = unittest.defaultTestLoader.discover(case_path, pattern="test_*.py")
        # discover()方法会自动根据测试目录中寻找所有与test_*.py名称模式匹配的测试用例文件,并加载其内容
        runner = unittest.TextTestRunner(verbosity=2)  # TextTestRunner类将用例执行的结果以text形式输出，分为0-6级，其中0最简单，1是默认值，2表示输出完整信息
        runner.run(discover)#run()方法执行discover
if __name__ == '__main__':
    unittest.main()
