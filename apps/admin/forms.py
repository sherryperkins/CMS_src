#encoding:utf-8
from wtforms import Form
from wtforms import StringField, BooleanField # 导入用到的字段
from wtforms.validators import InputRequired, Length, Email # 导入用到的验证器

class LoginForm(Form):

    username= StringField(
        label='用户名',
        validators=[
            InputRequired('用户名为必填项'),
            Length(4, 20, '密码长度为4到20')
        ]
    )
    password = StringField(
        label='密码',
        validators=[
            InputRequired('密码为必填项'),
            Length(6, 9, '密码长度为6到9')
        ]
    )
    sex = StringField(validators=[Length(0, 2, message='性别长度为1-2位')])
    telephone = StringField(validators=[Length(0,11, message='电话长度为1-11位')])
    status = StringField(validators=[Length(0, 2, message='启用状态长度为1-2位')])
    role_id = StringField(validators=[Length(0, 10, message='角色为1-10位')])
    email = StringField(validators=[Length(0, 100, message='邮箱为1-100位')])
    remarks=StringField(validators=[Length(0, 500, message='邮箱为0-500位')])
class Article_cat(Form):
    parent_id = StringField(validators=[Length(1, 20, message='父栏目长度为1-20位')])
    cat_name = StringField(validators=[Length(1, 100, message='栏目名字长度为1-100位')])
    dir = StringField(validators=[Length(0, 100, message='别名长度为0-100位')])
    keywords = StringField(validators=[Length(1, 100, message='关键字长度为1-100位')])
    description= StringField(validators=[Length(1, 100, message='栏目描述长度为1-200位')])
    cat_sort = StringField(validators=[Length(1, 100, message='栏目排序长度为1-5位')])
class Article(Form):
    cat_id = StringField(validators=[Length(1, 20, message='栏目为1-20位')])
    title=StringField(validators=[Length(2,120,message='文章标题长度为2-120位')])
    shorttitle=StringField(validators=[Length(2,20,message='短标题长度为2-20位')])
    source=StringField(validators=[Length(1,50,message='短标题长度为1-50位')])
    keywords=StringField(validators=[Length(1,30,message='关键字长度为1-30位')])
    description=StringField(validators=[Length(0,400,message='摘要长度为0-400位')])
    body=StringField(validators=[Length(0,20000000,message='摘要长度为0-20000000')])
    picture=StringField(validators=[Length(1,200,message='缩略图长度为1-200位')])
    author_id=StringField(validators=[Length(1,30,message='作者名字长度需要1-30位长度')])
    allowcomments=StringField(validators=[Length(1,2,message='允许评论长度为1-2位')])
    status=StringField(validators=[Length(1,2,message='发布状态长度为1-2位')])
class Checek_Auth(Form):
    url = StringField(validators=[Length(1, 100, message='父栏目长度为1-100位')])
    name = StringField(validators=[Length(1, 100, message='栏目名字长度为1-100位')])
    parent_id = StringField(validators=[Length(1, 30, message='上级栏目长度为1-100位')])
    status = StringField(validators=[Length(1, 6, message='上级栏目长度为1-6位')])
#角色表单验证
class Checek_Role(Form):
    auths = StringField(validators=[Length(1, 100, message='父栏目长度为1-100位')])
    name = StringField(validators=[Length(1, 100, message='栏目名字长度为1-100位')])
    description = StringField(validators=[Length(1, 300, message='上级栏目长度为1-100位')])


