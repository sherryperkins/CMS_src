#encoding:utf-8
from flask import Blueprint,render_template,request,session,redirect,url_for,make_response,jsonify,json
from .models import Users,Articles_Cat,Articles_Tag,Articles,Comment,Operate_Log,Admin_Log,Auth,Role
from .forms import LoginForm,Article_cat,Article,Checek_Auth,Checek_Role
from utils.captcha import create_validate_code
from io import BytesIO
from datetime import timedelta
from .decorators import login_required,admin_auth
from exts import db
from xpinyin import Pinyin
from sqlalchemy import func#统计查询使用
from sqlalchemy import and_#多个添加查询
from .recursion import creat_commont_tree,creat_table,build_auth_tree,build_auth_table,creat_auth_table
from .functional import get_auths,test_auths
import config
import os
from flask_wtf.csrf import generate_csrf
import time, datetime
import re
import memcache
bp=Blueprint("admin", __name__,url_prefix='/admin')
@bp.route("/login/",methods=['GET', 'POST'])
def login():
    error = None
    # print(session.get('user_id'))
    if request.method == 'GET':
        return  render_template('admin/login.html')
    else:
        form=LoginForm(request.form)
        if form.validate():
                user = request.form.get('username')
                pwd = request.form.get('password')
                online=request.form.get('online')
                captcha=request.form.get('captcha')
                mc = memcache.Client(['127.0.0.1:11211'], debug=True)
                if mc.get('image'):  # 如果memcache存在验证码
                    captcha_code = mc.get('image').lower()  # .lower()函数是把值转换成小写形式
                else:
                    captcha_code = session.get('image').lower()
                    if captcha_code != captcha.lower():
                    # if session.get('image').lower() != captcha.lower():
                        return render_template('admin/login.html', message="验证码不对！")
                    else:
                            users=Users.query.filter_by(username=user).first()
                            if users:
                                        if user == users.username and users.check_password(pwd):
                                            #session['user_id'] = users.uid#用户id存于session
                                            session[config.ADMIN_USER_ID] = users.uid
                                            # 记录该操作，生成日志
                                            user_id = session.get(config.ADMIN_USER_ID)
                                            oplog = Admin_Log(
                                                admin_id=user_id,
                                                ip=request.remote_addr,
                                                time=time.time(),
                                                operate="用户:" + users.username + "进行了登录操作！"
                                            )
                                            db.session.add(oplog)
                                            db.session.commit()
                                            # 记录该操作，生成日志完毕
                                            if online:#如果选择了记住我
                                                session.permanent = True
                                                bp.permanent_session_lifetime = timedelta(days=10)

                                            return redirect(url_for('admin.index'))
                                        else:
                                            #print("用户名或密码错！")
                                            error="用户名或密码错！"
                                            return render_template('admin/login.html', message=error)
                            else:
                                return render_template('admin/login.html', message="别试了，没有此用户！")
        else:
               return render_template('admin/login.html', message=form.errors)
@bp.route('/')
@login_required
def index():
    auths=get_auths(1)
    result=test_auths(1)
    return render_template('admin/index_new.html',auths=auths,result=result)
#调用验证码
@bp.route('/code/')
def get_code():
    # 把strs发给前端,或者在后台使用session保存
    code_img, strs = create_validate_code()
    buf=BytesIO()
    code_img.save(buf, 'JPEG', quality=70)
    buf_str = buf.getvalue()
    # buf.seek(0)
    response = make_response(buf_str)
    response.headers['Content-Type'] = 'image/jpeg'
    # 将验证码字符串储存在session中
    session['image'] = strs
    # 把验证码存入memcache中
    mc = memcache.Client(['127.0.0.1:11211'], debug=True)  # 链接memcache服务器
    mc.add('image', strs, time=300)  # 过期时间5分钟
    return response
@bp.route('/test/')
@login_required
def test():
    return 'test index'
@bp.route('/logout/')
@login_required
def logout():
    # del session[config.ADMIN_USER_ID]
    # 记录该操作，生成日志
    user_id = session.get(config.ADMIN_USER_ID)
    users=Users.query.filter(Users.uid==user_id).first()
    oplog = Admin_Log(
        admin_id=user_id,
        ip=request.remote_addr,
        time=time.time(),
        operate="用户:" + users.username + "进行了注销操作！"
    )
    db.session.add(oplog)
    db.session.commit()
    # 记录该操作，生成日志完毕
    session.pop(config.ADMIN_USER_ID, None)
    return redirect(url_for('admin.login'))
#登录页视图
@bp.route('/welcome/')
@login_required
def welcome():
    return  render_template('admin/welcome.html')
#个人信息页视图
@bp.route('/profile/')
@login_required
def profile():
    #根据session取得用户信息
    if config.ADMIN_USER_ID  in session:
        user_id = session.get(config.ADMIN_USER_ID)
        user = Users.query.get(user_id)

    return render_template('admin/profile.html',user=user)
#管理员修改密码
@bp.route('/editpwd/',methods=['GET', 'POST'])
@login_required
def editpwd():
    if request.method == 'GET':
        return render_template('admin/edit_pwd.html')
    else:
        oldpwd = request.form.get('oldpwd')
        newpwd1 = request.form.get('newpwd1')
        newpwd2 = request.form.get('newpwd2')
        print(oldpwd)
        user_id = session.get(config.ADMIN_USER_ID)
        user = Users.query.filter_by(uid=user_id).first()
        user.password = newpwd1
        db.session.commit()
        return render_template('admin/edit_pwd.html',message="密码修改成功！")
#核实校验密码
@bp.route('/checkpwd/')
@login_required
def checkpwd():
    # user1 = request.args.get('username')
    oldpwd = request.args.get('oldpwd', '')
    # print(oldpwd)
    if config.ADMIN_USER_ID  in session:
        user_id = session.get(config.ADMIN_USER_ID)
        user = Users.query.filter_by(username='admin').first()
        if user.check_password(oldpwd):
            data = {
                    "name": user.email,
                   "status": 11
                  }
        else:
            data = {
                "name": None,
                "status": 00
            }
    return jsonify(data)

def build_tree(data,p_id,level=0):
    """
    生成树菜单
    :param data:    数据
    :param p_id:    上级分类
    :param level:   当前级别
    :return:
    """
    tree = []
    for row in data:
        if row['parent_id'] ==p_id:
            row['level'] = level
            child = build_tree(data, row['cat_id'], level+1)
            row['child'] = []
            if child:
                row['child'] += child
            tree.append(row)

    return tree
#生成分类
def build_table(data, parent_title='顶级菜单'):
    html = ''
    for row in data:
        splice = '├ '
        cat_id=row['cat_id']
        title = splice * row['level'] + row['cat_name']
        tr_td = """<option value={cat_id}>  {title}</option>
                                   """
        if row['child']:
            html += tr_td.format(class_name='top_menu', title=title,cat_id=cat_id)
            html += build_table(row['child'], row['cat_name'])
        else:
            html += tr_td.format(class_name='', title=title,cat_id=cat_id)
            # return html
    return html
#生成分类列表
def creat_cat_list(data, parent_title='顶级菜单'):
    html = ''
    for row in data:
        splice = '-- '
        cat_id=row['cat_id']
        cat_sort = row['cat_sort']
        title = splice * row['level'] + row['cat_name']
        description = row['description']
        dir = row['dir']
        tr_td = """<tr>
        <td align="left"> <a href="article.php?cat_id={cat_id}"></a>{title}</td>
        <td>{dir}</td>
        <td>{description}</td>
        <td align="center">{cat_sort}</td>
        <td align="center"><a href="../article_cat_edit/{cat_id}" >编辑</a>| <a href="../article_cat_del/{cat_id}" onClick="rec();return false">删除</a> </td>
      </tr>
                                   """


        if row['child']:
            html += tr_td.format(class_name='', title=title,cat_id=cat_id, description= description,dir=dir,cat_sort=cat_sort)
            html += creat_cat_list(row['child'], row['cat_name'])
        else:
            html += tr_td.format(class_name='-', title=title,cat_id=cat_id,description= description,dir=dir,cat_sort=cat_sort)
            # return html
    return html

#添加分类
@bp.route('/article_cat_add/',methods=['GET', 'POST'])
@login_required
def article_cat_add():
    if request.method == 'GET':
        categorys=Articles_Cat.query.all()#取得所有分类
        list = []
        data =  {}

        for cat in categorys:
            data=dict(cat_id=cat.cat_id, parent_id=cat.parent_id,cat_name=cat.cat_name)
            list.append(data)
        data=build_tree(list,0,0)
        print(data)
        # print(list)
        html=build_table(data, parent_title='顶级菜单')
        # print(html)
        return render_template('admin/article_cat.html',message=html)#article_cat.html
    else:
        form=Article_cat(request.form)
        p = Pinyin()
        dir = request.form.get('dir')
        print(dir)
        if form.validate():
            parent_id = request.form.get('parent_id')
            cat_name = request.form.get('cat_name')
            dir = request.form.get('dir')
            check=request.form.get('check')
            if check:
                dir = request.form.get('cat_name')
                dir=p.get_pinyin(dir, '')
            else:
                if dir:
                    dir = request.form.get('dir')
                else:
                    dir = request.form.get('cat_name')
                    dir = p.get_pinyin(dir, '')
            keywords = request.form.get('keywords')
            description = request.form.get('description')
            cat_sort = request.form.get('cat_sort')
            status= request.form.get('status')
            insert = Articles_Cat(parent_id=parent_id, cat_name=cat_name, dir=dir, keywords=keywords,description=description, cat_sort=cat_sort,status=status)
            db.session.add(insert)
            db.session.commit()
            return redirect(url_for('admin.article_cat_list'))
        else:
            print("校验没有通过")
            return "校验没通过 "
#栏目列表
@bp.route('/article_cat_list/',methods=['GET'])
@login_required
@admin_auth
def article_cat_list():
    if request.method == 'GET':
        categorys = Articles_Cat.query.all()  # 取得所有分类
        list = []
        data = {}

        for cat in categorys:
            data = dict(cat_id=cat.cat_id, parent_id=cat.parent_id, cat_name=cat.cat_name,description=cat.description,dir=cat.dir,cat_sort=cat.cat_sort)
            list.append(data)
        data = build_tree(list, 0, 0)
        html = creat_cat_list(data, parent_title='顶级菜单')
        return render_template('admin/articel_cat_list.html',message=html)
#文章栏目编辑并保存
@bp.route('/article_cat_edit/<id>/', methods=['GET','POST'])
@login_required
def article_cat_edit(id):
    if request.method == 'GET':
        cat_list = Articles_Cat.query.filter_by(cat_id=id).first()
        categorys = Articles_Cat.query.all()  # 取得所有分类
        list = []
        data = {}
        for cat in categorys:
            data = dict(cat_id=cat.cat_id, parent_id=cat.parent_id, cat_name=cat.cat_name)
            list.append(data)
        data = build_tree(list, 0, 0)
        html = build_table(data, parent_title='顶级菜单')
        return render_template('admin/articel_cat_edit.html',content=cat_list,message=html)
    else:
        form = Article_cat(request.form)
        p = Pinyin()
        if form.validate():
            parent_id = request.form.get('parent_id')
            print(parent_id)
            cat_id = int(request.form.get('cat_id'))
            cat_name = request.form.get('cat_name')
            dir = request.form.get('dir')
            check = request.form.get('check')
            if check:
                dir = request.form.get('cat_name')
                dir = p.get_pinyin(dir, '')
            else:
                if dir:
                    dir = request.form.get('dir')
                else:
                    dir = request.form.get('cat_name')
                    dir = p.get_pinyin(dir, '')
            keywords = request.form.get('keywords')
            description = request.form.get('description')
            cat_sort = request.form.get('cat_sort')
            status = request.form.get('status')
            Articles_Cat.query.filter(Articles_Cat.cat_id == cat_id).update(
                {Articles_Cat.parent_id: parent_id, Articles_Cat.cat_name: cat_name, Articles_Cat.dir: dir, \
                 Articles_Cat.keywords: keywords, Articles_Cat.description: description,
                 Articles_Cat.cat_sort: cat_sort, Articles_Cat.status: status \
                 })
            db.session.commit()
            return redirect(url_for('admin.article_cat_list'))
#文章栏目修改保存
@bp.route('/article_cat_save/', methods=['POST'])
@login_required
def article_cat_save():
    form = Article_cat(request.form)
    p = Pinyin()
    if form.validate():
        parent_id = request.form.get('parent_id')
        print(parent_id)
        cat_id = int(request.form.get('cat_id'))
        cat_name = request.form.get('cat_name')
        dir = request.form.get('dir')
        check = request.form.get('check')
        if check:
            dir = request.form.get('cat_name')
            dir = p.get_pinyin(dir, '')
        else:
            if dir:
                dir = request.form.get('dir')
            else:
                dir = request.form.get('cat_name')
                dir = p.get_pinyin(dir, '')
        keywords = request.form.get('keywords')
        description = request.form.get('description')
        cat_sort = request.form.get('cat_sort')
        status = request.form.get('status')
        Articles_Cat.query.filter(Articles_Cat.cat_id==cat_id).update({Articles_Cat.parent_id: parent_id,Articles_Cat.cat_name: cat_name,Articles_Cat.dir: dir, \
                                 Articles_Cat.keywords: keywords,Articles_Cat.description: description, Articles_Cat.cat_sort: cat_sort, Articles_Cat.status: status\
                                                                       })
        db.session.commit()
        return redirect(url_for('admin.article_cat_list'))

#文章栏目删除
@bp.route('/article_cat_del/<id>', methods=['GET'])
@login_required
def article_cat_del(id):
    cat1 = Articles_Cat.query.filter(Articles_Cat.cat_id == id).first()  # 查询出数据库中的记录
    db.session.delete(cat1)
    db.session.commit()
    return redirect(url_for('admin.article_cat_list'))
#添加文章
@bp.route('/article_add', methods=['GET','POST'])
@login_required
@admin_auth
def article_add():
    if request.method == 'GET':
        categorys = Articles_Cat.query.all()  # 取得所有分类
        list = []
        data = {}
        for cat in categorys:
            data = dict(cat_id=cat.cat_id, parent_id=cat.parent_id, cat_name=cat.cat_name)
            list.append(data)
        data = build_tree(list, 0, 0)
        html = build_table(data, parent_title='顶级菜单')
        return render_template('admin/article-add.html',cat=html)
    else:
        form=Article(request.form)
        if form.validate():
            title=request.form['title']
            shorttitle=request.form['shorttitle']
            cat_id=request.form['cat_id']
            keywords = request.form['keywords']
            description = request.form['description']
            author_id=request.form['author_id']
            user_id = session.get(config.ADMIN_USER_ID)
            author_id=user_id
            source=request.form['source']
            allowcomments = request.form['allowcomments']
            status = request.form.get('status')
            picture = request.form['picture']
            body = request.form['editorValue']
            article1 =Articles(title=title, shorttitle=shorttitle, cat_id=cat_id, keywords=keywords,description=description,author_id=author_id,
                            source=source,allowcomments=allowcomments,status=status,picture=picture,body=body)
            db.session.add(article1)
            db.session.commit()
            rows = Articles.query.filter(Articles.status == 0).all()
            return render_template('admin/article-list.html',rows=rows)

        else:
            # 验证失败
            errors=form.errors
            return render_template('admin/article-add.html', errors=errors)
#文章列表
@bp.route('/article_list', methods=['GET','POST'])
def article_list():
    if request.method=='GET':
        rows=db.session.query(Articles).filter(Articles.is_delete==0).all()
        #获取总的记录
        # total1=db.session.execute('select count(*) from jq_article where status=0').first()
        total=db.session.query(func.count(Articles.aid)).filter(Articles.is_delete==0).scalar()
        return render_template('admin/article-list.html',rows=rows,total=total,)
#删除某条文章
@bp.route('article_del',methods=['GET','POST'])
def article_del():
    if request.method=='POST':
        id = request.values.get('aid')#接收字典数据
        db.session.query(Articles).filter_by(aid=id).update({Articles.is_delete:1})
        db.session.commit()
        data = {
            "msg": "保存成功",
            "success": 1
        }
    return jsonify(data)
#批量删除文章
@bp.route('article_all_del',methods=['GET','POST'])
def article_all_del():
    if request.method=='POST':
        id=request.values.get('aid')
        # print(id)
        artilces = db.session.query(Articles).filter(Articles.aid.in_(id)).all()
        for art in artilces:
            art.is_delete=1
            db.session.commit()
        data = {
            "msg": "保存成功",
            "success": 1
        }
    return jsonify(data)
#编辑修改文章
@bp.route('article_edit/<id>',methods=['GET'])
def article_edit(id):
    if request.method=='GET':
         #取得栏目列表
         categorys = Articles_Cat.query.all()  # 取得所有分类
         list = []
         data = {}
         for cat in categorys:
             data = dict(cat_id=cat.cat_id, parent_id=cat.parent_id, cat_name=cat.cat_name)
             list.append(data)
         data = build_tree(list, 0, 0)
         html = build_table(data, parent_title='顶级菜单')
         article = Articles.query.filter(Articles.aid == id).first()  # 查询出要修改的记录
         #获取用户名
         user=Users.query.filter(Users.uid==article.author_id).first()
         if user:
             username = user.username
         else:
             username='admin'

         return render_template('admin/article-edit.html',article=article,cat=html,username=username)
#保存编辑后的文章
@bp.route('article_edit_save',methods=['POST'])
def article_edit_save():
    errors = None
    if request.method == 'POST':
        form = Article(request.form)
        if form.validate():
            id = request.form['article_id']
            title = request.form['title']
            shorttitle = request.form['shorttitle']
            cat_id = request.form['cat_id']
            keywords = request.form['keywords']
            description = request.form['description']
            author_id = request.form['author_id_new']
            source = request.form['source']
            allowcomments = request.form['allowcomments']
            status = request.form.get('status')
            picture = request.form['picture']
            body = request.form['editorValue']
            Articles.query.filter(Articles.aid == id).update(
                {Articles.title: title, Articles.shorttitle: shorttitle, Articles.cat_id: cat_id, \
                 Articles.keywords: keywords, Articles.description: description, Articles.author_id: author_id, \
                 Articles.source: source, Articles.allowcomments: allowcomments, Articles.status: status, \
                 Articles.picture: picture, Articles.body: body
                 })
            db.session.commit()
        else:
            # 验证失败
            if form.errors:
                errors=form.errors
            else:
                errors = None

            print(errors)
        data = {
            "msg": "修改成功",
            "success": 1,
            "errors":errors
        }
    return jsonify(data)
#搜索处理
@bp.route('/search_list/',methods=['GET','POST'])
def search_list():
    PAGESIZE=2#分页大小，每页显示2条
    current_page=1#当前第几页，默认第一页
    count=0#总记录数
    total_page=0#一共有多少页
    if request.method=='GET':
        current_page = request.args.get("p", '')  # 传过来第几页数 current_page
        key=request.args.get("key",'')
        show_shouye_status = 0  # 显示首页状态

        if current_page == '':
            current_page = 1
        else:
            current_page = int(current_page)
            if current_page > 1:
                show_shouye_status = 1
        #获取总记录数
        # count = db.session.query(func.count(Articles.aid)).filter(Articles.status == 0).scalar()
        count = db.session.query(func.count(Articles.aid)).filter(Articles.status == 0).filter(Articles.title.like('%'+key+'%')).scalar()
        #获取分页数
        zone=int(count%PAGESIZE)
        if zone==0:
            total_page=int(count/PAGESIZE)
        else:
            total_page = int(count/PAGESIZE +1)
            # article=Articles.query.filter(Articles.status==0).all()
        arts=db.session.query(Articles).filter(Articles.status == 0).filter(Articles.title.like('%'+key+'%')).limit(PAGESIZE).offset((int(current_page) - 1) * PAGESIZE).all()
        datas = {
            'user_list': 'admin/search_list/',#http://127.0.0.1:5000/admin/search_list/?p=2
            'p': int(current_page),
            'total': total_page,
            'count': count,
            'show_shouye_status': show_shouye_status,
            'dic_list': arts

        }
        return render_template('admin/search_list.html',datas=datas,key=key)
#资讯下架
@bp.route('article_stop',methods=['POST'])
def article_stop():
    id=int(request.values.get('aid'))
    db.session.query(Articles).filter_by(aid=id).update({Articles.status: -1})
    data = {
        "msg": "修改成功",
        "success": 1,
        "errors": "错误"
    }
    return jsonify(data)
#资讯发布审核
@bp.route('article_start',methods=['POST'])
def article_start():
    id=int(request.values.get('aid'))
    db.session.query(Articles).filter_by(aid=id).update({Articles.status: 0})
    data = {
        "msg": "修改成功",
        "success": 1,
        "errors": "错误"
    }
    return jsonify(data)
@bp.after_request
def after_request(response):
    # 调用函数生成 csrf_token
    csrf_token = generate_csrf()
    # 通过 cookie 将值传给前端
    response.set_cookie("csrf_token", csrf_token)
    return response
#评论列表
@bp.route('/comment_list/',methods=['GET'])
def comment_list():
    #添加测试数据
    test_commont=Comment(
        aid=2,
        title ="测试1",
        user_id = 1,
        user_name = "admin",
        comment = "评论数据1",
        status = 0,
        parent_id = 0,
        comment_ip = request.remote_addr
    )
    test_commont1 = Comment(
        aid=2,
        title="测试1",
        user_id=2,
        user_name="admin",
        comment="评论数据1",
        status=0,
        parent_id=0,
        comment_ip=request.remote_addr
    )
    test_commont2 = Comment(
        aid=2,
        title="测试1",
        user_id=1,
        user_name="admin",
        comment="评论数据2",
        status=0,
        parent_id=1,
        comment_ip=request.remote_addr
    )
    test_commont3 = Comment(
        aid=2,
        title="测试1",
        user_id=1,
        user_name="admin",
        comment="评论数据3",
        status=0,
        parent_id=1,
        comment_ip=request.remote_addr
    )
    test_commont4 = Comment(
        aid=2,
        title="测试4",
        user_id=1,
        user_name="admin",
        comment="评论数据4",
        status=0,
        parent_id=0,
        comment_ip=request.remote_addr
    )

    test_commont6 = Comment(
        aid=2,
        title="测试6",
        user_id=1,
        user_name="admin",
        comment="评论数据6",
        status=0,
        parent_id=0,
        comment_ip=request.remote_addr
    )
    test_commont7 = Comment(
        aid=2,
        title="测试7",
        user_id=1,
        user_name="admin",
        comment="评论数据7",
        status=0,
        parent_id=0,
        comment_ip=request.remote_addr
    )

    # db.session.add(test_commont1)
    # db.session.add(test_commont2)
    # db.session.add(test_commont7)
    # db.session.commit()
    PAGESIZE = 2  # 分页大小，每页显示2条
    current_page = 1  # 当前第几页，默认第一页
    count = 0  # 总记录数
    total_page = 0  # 一共有多少页
    list = []#列表
    data = {}#字典
    list1=[]
    if request.method == 'GET':
        current_page = request.args.get("p", '')  # 传过来第几页数 current_page
        show_shouye_status = 0  # 显示首页状态
        is_end_page=0#是否是尾页
        if current_page == '':
            current_page = 1
        else:
            current_page = int(current_page)
            if current_page > 1:
                show_shouye_status = 1
        # 获取总记录数
        count = db.session.query(func.count(Comment.id)).filter(Comment.parent_id == 0).scalar()
        # 获取分页数
        zone = int(count % PAGESIZE)
        if zone == 0:
            total_page = int(count / PAGESIZE)
        else:
            total_page = int(count / PAGESIZE + 1)
        if current_page == total_page:
            is_end_page=1
        else:
            is_end_page =0
        commonts=Comment.query.filter(Comment.parent_id==0).limit(PAGESIZE).offset((int(current_page) - 1) * PAGESIZE).all()
        for row1 in commonts:
            list1.append(row1)
            commonts1 = Comment.query.filter(Comment.parent_id == row1.id).all()
            for row2 in commonts1:
                list1.append(row2)
        for comment2 in list1:
            #获取评论详情
            data = dict(id=comment2.id, aid=comment2.aid, title=comment2.title, user_id=comment2.user_id,
                        user_name=comment2.user_name, comment=comment2.comment, \
                        parent_id=comment2.parent_id, status=comment2.status,add_time=comment2.add_time,comment_ip=comment2.comment_ip)
            list.append(data)
        zz=creat_commont_tree(list,0,0)
        html = creat_table(zz, parent_title='顶级菜单')
        datas = {
            'page_list': 'admin/comment_list/',  # http://127.0.0.1:5000/admin/commet_list/?p=2
            'p': int(current_page),
            'total': total_page,
            'count': count,
            'show_shouye_status': show_shouye_status,
            'is_end_page':is_end_page,
            'dic_list': html

        }

        # return render_template('admin/admin_articel_common_list.html',datas=datas)
        return render_template('admin/admin_articel_comment_list.html',datas=datas)
#评论审核-下线
@bp.route('comment_stop/',methods=['POST'])
def comment_stop():
        id = int(request.values.get('aid'))
        db.session.query(Comment).filter_by(id=id).update({Comment.status: -1})
        #记录该操作，生成日志
        user_id = session.get(config.ADMIN_USER_ID)
        oplog = Operate_Log(
            admin_id=user_id,
            ip=request.remote_addr,
            operate="id为:"+str(id) +"的评论被设置下线！"
        )
        db.session.add(oplog)
        db.session.commit()
        # 记录该操作，生成日志完毕
        data = {
            "msg": "修改成功",
            "success": 1,
            "errors": "错误"
        }
        return jsonify(data)
#评论审核-上线
@bp.route('comment_start/',methods=['POST'])
def comment_start():
        id = int(request.values.get('aid'))
        db.session.query(Comment).filter_by(id=id).update({Comment.status: 0})
        # 记录该操作，生成日志
        user_id = session.get(config.ADMIN_USER_ID)
        oplog = Operate_Log(
            admin_id=user_id,
            ip=request.remote_addr,
            operate="id为:" +str(id)  + "的评论被设置上线！"
        )
        db.session.add(oplog)
        db.session.commit()
        # 记录该操作，生成日志完毕
        data = {
            "msg": "修改成功",
            "success": 1,
            "errors": "错误"
        }
        return jsonify(data)
#评论审核-删除
@bp.route('comment_del/',methods=['POST'])
def comment_del():
        id = int(request.values.get('aid'))
        comment1=db.session.query(Comment).filter_by(id=id).first()
        db.session.delete(comment1)
        db.session.commit()
        # 记录该操作，生成日志
        user_id = session.get(config.ADMIN_USER_ID)
        oplog = Operate_Log(
            admin_id=user_id,
            ip=request.remote_addr,
            operate="id为:" +str(id) + "的评论被删除！"
        )
        db.session.add(oplog)
        db.session.commit()
        # 记录该操作，生成日志完毕

        data = {
            "msg": "修改成功",
            "success": 1,
            "errors": "错误"
        }
        return jsonify(data)
#登录日志列表
@bp.route('/admin_log_list/',methods=['GET','POST'])
@login_required
@admin_auth
def admin_log_list():
    if request.method=='GET':
        list=[]
        data={}
        current_page = request.args.get("p", '')
        # 分页逻辑开始
        PAGESIZE = 2  # 分页大小
        show_shouye_status = 0  # 显示首页状态
        is_end_page = 0  # 是否是尾页
        if current_page == '':
            current_page = 1
        else:
            current_page = int(current_page)
            if current_page > 1:
                show_shouye_status = 1
        # 获取总记录数
        count = db.session.query(func.count(Admin_Log.id)).scalar()
        # 获取分页数
        zone = int(count % PAGESIZE)
        if zone == 0:
            total_page = int(count / PAGESIZE)
        else:
            total_page = int(count / PAGESIZE + 1)
        if current_page == total_page:
            is_end_page = 1
        else:
            is_end_page = 0
        admin_logs=db.session.query(Admin_Log).limit(PAGESIZE).offset((int(current_page) - 1) * PAGESIZE).all()
        for v in admin_logs:
            user = db.session.query(Users).filter(Users.uid == v.admin_id).first()
            data={
                'id':v.id,
                'operate':v.operate,
                'ip': v.ip,
                'add_time': v.add_time,
                'user_name':user.username
            }
            list.append(data)
        datas = {
            'user_list': '/admin/admin_log_list/',
            'p': int(current_page),
            'total': total_page,
            'count': count,
            'show_shouye_status': show_shouye_status

        }

        return  render_template('admin/admin_system_log.html',list=list,count=count,datas=datas)
#删除指定登录日志
@bp.route('/admin_log_del/',methods=['GET','POST'])
def admin_log_del():
    id = int(request.values.get('aid'))
    comment1 = db.session.query(Admin_Log).filter_by(id=id).first()
    db.session.delete(comment1)
    db.session.commit()
    data = {
        "msg": "修改成功",
        "success": 1
    }
    return jsonify(data)
    return redirect(url_for('admin_log_list'))
#批量删除指定登录日志
@bp.route('/system_log_all_del/',methods=['GET','POST'])
def system_log_all_del():
    list1=[]
    id=str(request.values.get('aid'))
    id=id.strip(',').split(',')#实现字符串转换成列表 实现str转换list
    # 获取总记录数
    count = db.session.query(func.count(Admin_Log.id)).scalar()
    adminlog = db.session.query(Admin_Log).filter(Admin_Log.id.in_(id)).all()
    for v in adminlog:
        db.session.delete(v)
        db.session.commit()

    data = {
        "msg": "修改成功",
        "success": 1
    }
    return jsonify(data)
    return redirect(url_for('admin_log_list'))
#一键清空登录日志
@bp.route('/admin_log_all_clear/',methods=['POST'])
def admin_log_all_clear():
    if request.method=='POST':
        order=request.values.get('aid')
        if order=='all':
            admin_log=db.session.query(Admin_Log).all()
            for i in admin_log:
                print(i)
                # db.session.delete(i)
                # db.session.commit()
            data = {
                "msg": "修改成功",
                "success": 1
            }
    return jsonify(data)
    return redirect(url_for('admin_log_list'))
def timer_change(timer):
    timeArray = time.strptime(timer, "%Y-%m-%d %H:%M:%S")
    timeStamp = int(time.mktime(timeArray))
    return timeStamp
#日志搜索
@bp.route('/system_log_search/',methods=['GET','POST'])
def system_log_search():
    if request.method == 'GET':
        current_page = request.args.get("p", '')
        time_start=request.args.get("time_start",'')
        time_stop = request.args.get("time_stop", '')
        key = request.args.get("key", '')
        #分页逻辑开始
        PAGESIZE=2#分页大小
        show_shouye_status = 0  # 显示首页状态
        is_end_page=0#是否是尾页
        if current_page == '':
            current_page = 1
        else:
            current_page = int(current_page)
            if current_page > 1:
                show_shouye_status = 1
        # 获取总记录数
        count = db.session.query(func.count(Admin_Log.id)).filter(Admin_Log.add_time >= time_start).filter(
            Admin_Log.add_time <= time_stop) \
            .filter(Admin_Log.operate.like('%' + key + '%')).scalar()
        # 获取分页数
        zone = int(count % PAGESIZE)
        if zone == 0:
            total_page = int(count / PAGESIZE)
        else:
            total_page = int(count / PAGESIZE + 1)
        if current_page == total_page:
            is_end_page=1
        else:
            is_end_page =0
            # adminlogs = db.session.query(Admin_Log).filter(Admin_Log.add_time >= time_start).filter(Admin_Log.add_time<=time_stop)\
        #     .filter(Admin_Log.operate.like('%'+key+'%')).all()
        adminlogs = db.session.query(Admin_Log).filter(Admin_Log.add_time >= time_start).filter(
            Admin_Log.add_time <= time_stop) \
            .filter(Admin_Log.operate.like('%' + key + '%')).limit(PAGESIZE).offset((int(current_page) - 1) * PAGESIZE).all()

        list = []
        data = {}
        for v in adminlogs:
            user = db.session.query(Users).filter(Users.uid == v.admin_id).first()
            data = {
                'id': v.id,
                'operate': v.operate,
                'ip': v.ip,
                'add_time': v.add_time,
                'user_name': user.username
            }
            list.append(data)
        datas = {
            'user_list': '/admin/system_log_search/',
            'p': int(current_page),
            'total': total_page,
            'count': count,
            'show_shouye_status': show_shouye_status,
            'time_start': time_start,
            'time_stop': time_stop,
            'key': key

        }
        search = {
            'time_start': time_start,
            'time_stop': time_stop,
            'key': key
        }

    return render_template('admin/admin_system_log_search.html',list=list,search=search,count=count,datas=datas)





#权限列表
@bp.route('/admin_permission/')
def admin_permission():
    page = int(request.args.get('page', 1))
    paginate=Auth.query.order_by(Auth.id.desc()).paginate(page,4)
    arts = paginate.items
    # for i in arts:
    #     print(i.name)
    return render_template('admin/admin_permission.html',paginate=paginate,arts=arts)
#添加权限
@bp.route('/admin_add_permission/',methods=['GET','POST'])
def admin_add_permission():
    if request.method=='GET':
        auths =Auth.query.order_by(Auth.id.desc()).all()  # 取得所有权限分类
        list = []
        data = {}
        for cat in auths:
            data = dict(id=cat.id, parent_id=cat.parent_id, name=cat.name)
            list.append(data)
        data = build_auth_tree(list, 0, 0)
        html = build_auth_table(data, parent_title='顶级菜单')
        return render_template('admin/admin_add_permission.html',message=html)
    else:
        #表单验证
        forms=Checek_Auth(request.form)#从form中导入Auth
        if forms.validate():  # 提交的时候进行验证,如果数据能被所有验证函数接受，则返回true，否则返回false
            datas = forms.data  # 获取form数据信息
            auth1=Auth(
                name=datas['name'],
                url=datas['url'],
                parent_id=datas['parent_id'],
                status=datas['status'],

            )
            db.session.add(auth1)
            db.session.commit()
            data = {
                "msg": "提交成功",
                "status":"200"
            }
        else:
            data = {
                "msg": "表单验证失败",
                "status": "202"
            }
    return jsonify(data)
#编辑权限
@bp.route('/admin_edit_permission/',methods=['GET','POST'])
def admin_edit_permission():
    if request.method=='GET':
        #取得权限所有列表
        auths = Auth.query.order_by(Auth.id.desc()).all()  # 取得所有权限分类
        list = []
        data = {}
        for cat in auths:
            data = dict(id=cat.id, parent_id=cat.parent_id, name=cat.name)
            list.append(data)
        data = build_auth_tree(list, 0, 0)
        html = build_auth_table(data, parent_title='顶级菜单')
        id = request.args.get('id')
        if id!=None:
            id=int(id)
            global auth1
            auth1=db.session.query(Auth).filter(Auth.id==id).first()
            print(auth1.id)
            print(auth1.parent_id)

        data = {
            "msg": "参数获取成功",
            "status": "200"
        }

        return render_template('admin/admin_edit_permission.html',data=auth1,message=html)
    else:
        #表单验证
        forms=Checek_Auth(request.form)#从form中导入Auth
        if forms.validate():  # 提交的时候进行验证,如果数据能被所有验证函数接受，则返回true，否则返回false
            datas = forms.data  # 获取form数据信息
            url = request.form.get('url')
            id = int(request.values.get('id'))
            auth1=db.session.query(Auth).filter_by(id.Not.in_(id)).first()
            db.session.query(Auth).filter_by(id=id).update({Auth.name: datas['name'],Auth.url:datas['url'],Auth.parent_id:datas['parent_id'],Auth.status:datas['status']})
            db.session.commit()
            data = {
            "msg": "提交成功",
            "status":"200",
            }

        else:
            data = {
                "msg": "表单验证失败",
                "status": "202"
            }
    return jsonify(data)
#删除单个权限
@bp.route('/admin_del_permission/',methods=['POST'])
def admin_del_permission():
    if request.method=='POST':
        id=int(request.values.get(id))
        if id:
            auth1=db.session.query(Auth).filter(id=id).first()
            db.session.delete(auth1)
            db.session.commit()
            data = {
                "msg": "删除成功",
                "status": "200"
            }
            return jsonify(data)
        else:
            data = {
                "msg": "id参数不合法",
                "status": "202"
            }
            return jsonify(data)
#权限批量删除
@bp.route('/admin_del_all_permission/',methods=['POST'])
def admin_del_all_permission():
    if request.method=='POST':
        id1=[]
        id2=[]
        id = str(request.values.get('id'))
        id1 = id.strip(',').split(',')
        for v in id1:
            id2.append(int(v))
        if id:
            auth1=db.session.query(Auth).filter(Auth.id.in_(id2)).all()
            for i in auth1:
                db.session.delete(i)
                db.session.commit()
            data = {
                    "msg": "删除成功",
                    "sucess": "200"
                }
            return jsonify(data)
        else:
            data = {
                "msg": "id参数不合法",
                "status": "202"
            }
            return jsonify(data)
#权限搜索
@bp.route('/admin_search_permission/',methods=['GET','POST'])
def admin_search_permission():
    if request.method == 'GET':
        key=request.args.get('key')
        page = int(request.args.get('page',1))

        paginate=db.session.query(Auth).filter(Auth.name.like('%' + key + '%')).order_by(Auth.id.desc()).paginate(page,4)
        arts = paginate.items
            # for i in arts:
            #     print(i.name)
        return render_template('admin/admin_search_permission.html', paginate=paginate, arts=arts,key=key)
#添加角色
@bp.route('/admin_add_role/',methods=['GET','POST'])
def admin_add_role():
    if request.method=='GET':
        auths = Auth.query.order_by(Auth.id.desc()).all()  # 取得所有权限分类
        list = []
        data = {}
        for cat in auths:
            data = dict(id=cat.id, parent_id=cat.parent_id, name=cat.name)
            list.append(data)
        data = build_auth_tree(list, 0, 0)
        html = creat_auth_table(data, parent_title='顶级菜单')
        return render_template('admin/admin_add_role.html',message=html)
    if request.method == 'POST':
        form = Checek_Role(request.form)
        if form.validate():
            datas = form.data
            auths = datas['auths']
            name = datas['name']
            description = datas['description']
            insert = Role(auths=auths, name=name, description=description)
            db.session.add(insert)
            db.session.commit()
            data = {
                "msg": "提交成功",
                "status": 200,
            }
            return jsonify(data)
        else:
            data = {
                "msg": "表单验证失败",
                "status": 202,
            }
            return jsonify(data)

#角色列表
@bp.route('/admin_role_list',methods=['GET','POST'])
def admin_role_list():
    if request.method=='GET':
        list=[]
        data={}
        roles=db.session.query(Role).all()
        count = db.session.query(func.count(Role.id)).scalar()
        for i in roles:
            admin=db.session.query(Users).filter(Users.role_id==i.id).first()

            if admin==None:
                admin="暂无"
            else:
                admin=admin.username
            data={
                'id':i.id,
                'name':i.name,
                'description':i.description,
                'admin':admin,
            }
            list.append(data)
        return render_template('admin/admin_role.html',roles=list,count=count)
#角色编辑
@bp.route('/admin_edit_role/',methods=['GET','POST'])
def admin_edit_role():
    if request.method=='GET':
        auths = Auth.query.order_by(Auth.id.desc()).all()  # 取得所有权限分类
        list = []
        data = {}
        for cat in auths:
            data = dict(id=cat.id, parent_id=cat.parent_id, name=cat.name)
            list.append(data)
        data = build_auth_tree(list, 0, 0)
        html = creat_auth_table(data, parent_title='顶级菜单')
        id = request.args.get("id", '')
        if id:
            global  role
            role= db.session.query(Role).filter(Role.id == id).first()
        return render_template('admin/admin_edit_role.html', message=html,role=role)
    if request.method=='POST':
        form = Checek_Role(request.form)
        if form.validate():
            datas = form.data
            auths = datas['auths']
            name = datas['name']
            description = datas['description']
            id=request.values.get('id')
            db.session.query(Role).filter_by(id=id).update({Role.auths:auths,Role.name:name,Role.description:description})
            db.session.commit()
            data={
            "msg":"已经提交成功",
            'status':200,
            }
            return jsonify(data)
#删除角色
@bp.route('/admin_del_role/',methods=['POST'])
def admin_del_role():
    if request.method=='POST':
        id=request.values.get('id')
        role=db.session.query(Role).filter(Role.id==id).first()
        db.session.delete(role)
        db.session.commit()
        data={
            'msg':"已删除",
            'sucess':200
        }
        return jsonify(data)
#角色批量删除
@bp.route('/admin_del_all_role/',methods=['POST'])
def admin_del_all_role():
    if request.method=='POST':
        id1 = []
        id2 = []
        id = str(request.values.get('id'))
        id1 = id.strip(',').split(',')
        for v in id1:
            id2.append(int(v))
        if id:
            auth1 = db.session.query(Role).filter(Role.id.in_(id2)).all()
            for i in auth1:
                db.session.delete(i)
                db.session.commit()
        data = {
            "msg": "提交成功",
            "status": "200",
        }
    return jsonify(data)