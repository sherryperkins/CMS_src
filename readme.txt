1.可以切换到当前虚拟环境下，输入如下命令：
 (venv) J:\python project\cms\apps\test>python run_test.py
此时输出结果如下：
J:\python project\python3\venv\lib\site-packages\werkzeug\datastructure
DeprecationWarning: Using or importing the ABCs from 'collections' inst
om 'collections.abc' is deprecated, and in 3.8 it will stop working
  from collections import Container, Iterable, MutableSet
J:\python project\python3\venv\lib\site-packages\jinja2\utils.py:485: D
nWarning: Using or importing the ABCs from 'collections' instead of fro
tions.abc' is deprecated, and in 3.8 it will stop working
  from collections import MutableMapping
J:\python project\python3\venv\lib\site-packages\markupsafe\__init__.py
ecationWarning: Using or importing the ABCs from 'collections' instead
collections.abc' is deprecated, and in 3.8 it will stop working
  from collections import Mapping
J:\python project\python3\venv\lib\site-packages\sqlalchemy\engine\resu
: DeprecationWarning: Using or importing the ABCs from 'collections' in
from 'collections.abc' is deprecated, and in 3.8 it will stop working
  from collections import Sequence
test_index (test_jiaqi_index.JiaQiTest) ... set up
down
clearing...
ok
test_error_username_password (test_login.TestLogin) ... 测试用户登录开始
误的用户名或密码
J:\python project\python3\venv\lib\site-packages\flask_sqlalchemy\__ini
2: DeprecationWarning: time.clock has been deprecated in Python 3.3 and
removed from Python 3.8: use time.perf_counter or time.process_time ins
  context._query_start_time = _timer()
J:\python project\python3\venv\lib\site-packages\flask_sqlalchemy\__ini
4: DeprecationWarning: time.clock has been deprecated in Python 3.3 and
removed from Python 3.8: use time.perf_counter or time.process_time ins
  statement, parameters, context._query_start_time, _timer(),
../..\apps\front\views.py:251: DeprecationWarning: The 'warn' method is
ed, use 'warning' instead
  query.duration))
测试用户登录结束，可以清除相应的测试数据
clearing...
ok
----------------------------------------------------------------
Ran 2 tests in 0.231s
OK
