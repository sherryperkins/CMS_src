#encoding:utf-8
from flask import Blueprint,render_template,request,flash,redirect,url_for,session,abort,jsonify
from flask_wtf import CSRFProtect
from .forms import RegisterForm,LoginForm,CommentForm
from .models import Members
from .recursion import build_cat_tree,build_cat_table
import sys#要导入上级目录中的模块，可以使用sys.path
sys.path.append('../')
from ..admin.models import Articles,Articles_Cat,Users,Comment
from exts import db
from flask_wtf.csrf import generate_csrf
from flask_sqlalchemy import get_debug_queries
from logging.handlers import RotatingFileHandler
import logging
import time, datetime,os
from datetime import timedelta
import memcache
from config import MEMBER_USER_ID,FLASKY_DB_QUERY_TIMEOUT
bp=Blueprint("front",__name__)#前台访问不需要前缀
@bp.route('/')
def index():
    list=[]
    data = {}
    if request.method=='GET':
        nav=Articles_Cat.query.all()
        for cat in nav:
            data = dict(cat_id=cat.cat_id, parent_id=cat.parent_id, cat_name=cat.cat_name, )
            list.append(data)
        cat=build_cat_tree(list,0,0)
        zz = build_cat_table(cat, parent_title='顶级菜单')
    #新闻列表
    news1=Articles.query.all()
    return  render_template('front/index.html',cat=zz,news1=news1)
#注册
@bp.route('/register',methods=['GET','POST'])#定义路由，限制其访问方法
def register():#定义视图函数
    if request.method == 'GET':#如果访问方法为GET方法
        return render_template('front/register.html')#渲染模板
    if request.method=='POST':#如果访问方法为POST方法
        form = RegisterForm(request.form)#进行表单验证
        username=form.username.data#取得表单username的值放到username中
        password1=form.password1.data#取得表单password1的值放到password1中
        password2=form.password2.data#取得表单password2的值放到password2中
        email=form.email.data#取得表单email的值放到email中
        if password1!=password2:#如果输入的密码不一样
            flash('两次输入的密码不一样', 'error')#用消息闪现予以提示
        else:
            user=Members(username=username,password=password1,email=email
                         )#定义user对象，并对其属性赋值
            db.session.add(user)#插入数据库
            db.session.commit()#提交事务
            flash('注册成功，请登录！','ok')
        return redirect(url_for('front.register'))
#登录
@bp.route('/login',methods=['GET','POST'])#定义路由，限制其访问方法
def login():#定义视图函数
    if request.method == 'GET':#如果访问方法为GET方法
        url = request.args.get('url')#接收网址的参数
        if url=='/log_out':#如果收到的为url内容为/log_out，则处理成'/'
            url='/'
        if url==None:#url为空值的处理
            session['url']=None
        else:
            session['url'] = url#url为非空，直接存到session中
        return render_template('front/login.html')#渲染模板
    else:
        form=LoginForm(request.form)#验证登录表单
        if form.validate():#如果表单验证通过
            username = form.username.data#取得表单username的值放到username中
            password = form.password.data#取得表单的值放到username中
            users = Members.query.filter_by(username=username).first()#按用户名取得用户相关记录
            if users:#如果用户存在
                if username == users.username and users.check_password(password):#验证用户名和校验密码
                    session[MEMBER_USER_ID] = users.username#将username对应的信息存到session中
                    session.permanent = True#实现回话持久化
                    bp.permanent_session_lifetime = timedelta(days=7)#默认保持一周
                else:
                    flash('用户账号或密码错误','error')#如果用户密码不对，则用消息闪现机制予以提示
                    return redirect(url_for('front.login'))#登录失败，网页重新定位到用户登陆页
            else:#用户输入用户错
                flash('用户账号或密码错误', 'error')#如果用户输入用户名错，则用消息闪现机制予以提示
                return redirect(url_for('front.login'))#登录失败，网页重新定位到用户登陆页
        else:
            errors = form.errors#获取表单验证出错信息
            flash(errors,'error')#如果表单验证没有通过，则用消息闪现机制予以提示
            return redirect(url_for('front.login'))#登录失败，网页重新定位到用户登陆页
        username = session.get(MEMBER_USER_ID)#取得用户名
        session['username']=username#将username存入session中
        if session['url']==None:
            return render_template('front/index.html', username=username)#渲染模板
        else:
            return redirect(session['url'])#网页重定位到用户登录之前的页面
#注销登录
@bp.route('/log_out')
def log_out():
    session.pop(MEMBER_USER_ID, None)#清除session
    session.pop('username', None)#清除session
    return redirect(url_for('front.index'))#网页重定向
#搜索页面路由
@bp.route('/search')
def search():
    return render_template('front/search.html')
#文章详情页面路由
@bp.route('/article_details/<int:id>',methods=['GET','POST'])#定义路由和指定访问方法
def article_details(id):#定义视图函数
    if request.method=='GET':#如果访问方法为GET方法
        #取得新闻详情
        news1=Articles.query.filter(Articles.aid==id).first_or_404()
        #取得新闻的作者
        author1=Users.query.filter(Users.uid==news1.author_id).first()
        if author1:#如果author1不为空
            author = author1.username#从author1对象中取得其属性值作为author变量的值
        else:
            author='无名'#如果author1对象为空，则author直接赋值为无名
        # 更新点击次数
        db.session.query(Articles).filter_by(aid=id).update({Articles.clicks: Articles.clicks+1})
        db.session.commit()#提交事务
        # 取得上一条记录
        news2 = Articles.query.filter(Articles.aid < id).order_by(Articles.aid.desc()).first()
        #取得下一条记录
        news3 = Articles.query.filter(Articles.aid > id).order_by(Articles.aid.asc()).first()
        #热门资讯
        news4=Articles.query.filter(Articles.is_delete==0).order_by(Articles.clicks.desc()).limit(5)
        list = []#定义列表list
        data = {}#定义字典data
        nav = Articles_Cat.query.all()  # 取得所有分类
        for cat in nav:  # 遍历对象nav
            data = dict(cat_id=cat.cat_id, parent_id=cat.parent_id, cat_name=cat.cat_name, )  # 构造字典数据
            list.append(data)  # 将字典数据追加到列表中
        cat = build_cat_tree(list, 0, 0)  # 构造目录树
        zz = build_cat_table(cat, parent_title='顶级菜单')  # 构造含有CSS样式的下拉列表菜单


        return render_template('front/article_details.html', news1=news1, news2=news2, news3=news3, news4=news4,
                           author=author, cat=zz)

    else:
        if request.method=='POST':#如果访问方法为POST方法
            form = CommentForm(request.form)  # 实例化定义的添加评论表单;
            data = form.data#获取表单数据
            id = data['article_id']#从表单中取得article_id的值
            if session.get('username') == None:#用户没有登录，则跳转到登陆页面
                url=url_for('front.login') +'?url=article_details/'+id#构造重定向网址
                return redirect(url)#网页重定向
            if form.validate():#如果表单验证通过
                comment_content = data['comment_content']#从表单中取值赋给comment_content
                captcha = data['captcha']#从表单中取值赋给captcha
                id = data['article_id']#从表单中取值赋给id
                title = data['article_title']#从表单中取值赋给title
                if session.get('image').lower() != captcha.lower():#如果POST过来的验证码与sessin中的验证码不相等
                    flash('验证码不对', 'error')  # 如果表单验证没有通过，则用消息闪现机制予以提示

                else:  #准备提交表单信息
                    username=session.get('username')#从session中取得username
                    user=Members.query.filter(Members.username==username).first_or_404()#根据用户名取得用户ID
                    uid=user.uid

                    #准备POST的数据
                    post = Comment(
                        title=title,  # 评论的文章标题
                        aid=id,  # 评论的文章ID
                        comment=comment_content,  # 评论内容
                        status=0, # 评论审核转台
                        parent_id=1,  # 评论的层次关系
                        add_time=datetime.datetime.now(),
                        user_name=session.get('username'),  # 获取session
                        user_id=uid,#评论用户ID
                        comment_ip=request.remote_addr  # 评论者的IP地址
                    )
                    db.session.add(post)  # 添加评论
                    db.session.commit()  # 提交事务
                    flash('评论添加成功', 'ok')  # 消息闪现
                    return redirect(url_for('front.article_details',id=id))#网页重定位
            else:
                errors = form.errors  # 获取表单验证出错信息
                flash(errors, 'error') # 如果表单验证没有通过，则用消息闪现机制予以提示
                return redirect(url_for('front.article_details',id=id)) # 登录失败，网页重新定位到用户登陆页
#404等错误处理
@bp.app_errorhandler(404)
def error_404(error):
    return render_template('front/404.html'), 404
  #500等错误处理
@bp.app_errorhandler(500)
def error_500(error):
       return render_template('front/500.html'), 500
#钩子函数产生csrf_token
@bp.after_request
def after_request(response):
    # 调用函数生成 csrf_token
    csrf_token = generate_csrf()
    # 通过 cookie 将值传给前端
    response.set_cookie("csrf_token", csrf_token)

    return response
#记录慢查询
@bp.after_app_request
def after_request(response):
    formatter = logging.Formatter(  # 设定日志格式
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = RotatingFileHandler('slow_query.log', maxBytes=10000, backupCount=10)
    handler.setLevel(logging.WARN)
    handler.setFormatter(formatter)
    logger = logging.getLogger("logger")
    logger.addHandler(handler)
    for query in get_debug_queries():
        if query.duration >= FLASKY_DB_QUERY_TIMEOUT:
            logger.warn(
                ('\nContext:{}\nSLOW QUERY: {}\nParameters: {}\nSTART_TIME: {}\nDuration: {}\n').format(query.context,
                                                                                                        query.statement,
                                                                                                        query.parameters,
                                                                                                        query.start_time,
                                                                                                        query.duration))
    return response