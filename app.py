from flask import Flask
from apps.admin import bp as admin_bp#导入各个模块app
from apps.front import bp as front_bp
from apps.common import bp as common_bp
from apps.ueditor import bp as edtior_bp
from flask_wtf import CSRFProtect
from flask_wtf import CSRFProtect as WTF # 利用表单类去渲染模板时需要用到
from exts import db
def create_app():
        app = Flask(__name__)
        #注册蓝图
        app.register_blueprint(admin_bp)
        app.register_blueprint(front_bp)
        app.register_blueprint(common_bp)
        app.register_blueprint(edtior_bp)
        app.config.from_object('config')#使用模块的名字
        #WTF(app)
        CSRFProtect(app)
        db.init_app(app)
        return app
if __name__ == '__main__':
    app=create_app()
    app.run(host='127.0.0.1', port=8000, debug=True)
