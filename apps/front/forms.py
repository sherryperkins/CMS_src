#encoding:utf-8
from wtforms import Form
from wtforms import StringField, BooleanField,SubmitField # 导入用到的字段
from wtforms.validators import InputRequired, Length, Email,DataRequired # 导入用到的验证器

class RegisterForm(Form):
    username= StringField(
        label='用户名',
        validators=[
            InputRequired('用户名为必填项'),
            Length(6, 15, '密码长度为4到20')
        ]
    )
    password1 = StringField(
        label='密码',
        validators=[
            InputRequired('密码为必填项'),
            Length(6, 30, '密码长度为6到9')
        ]
    )
    password2 = StringField(
        label='密码',
        validators=[
            InputRequired('密码为必填项'),
            Length(6, 30, '密码长度为6到9')
        ]
    )
    email = StringField(validators=[Length(0, 100, message='邮箱为1-100位')])
class LoginForm(Form):
    username = StringField(
        label='用户名',
        validators=[
            InputRequired('用户名为必填项'),
            Length(6, 15, '密码长度为6到20')
        ]
    )
    password = StringField(
        label='密码',
        validators=[
            InputRequired('密码为必填项'),
            Length(6, 30, '密码长度为6到9')
        ]
    )
#评论表单验证
class CommentForm(Form):
    comment_content = StringField("评论内容：", validators=[DataRequired("请输入评论内容"),Length(1, 600)], render_kw={"placeholder": "请输入评论内容"})
    captcha = StringField("验证码：", validators=[DataRequired("请输入验证码")],render_kw={"placeholder": "请输入验证码"})
    article_id = StringField("文章ID：", validators=[DataRequired("请输入文章ID")],render_kw={"placeholder": "请输入文章ID"})
    article_title= StringField("文章标题：", validators=[DataRequired("请输入文章标题")],render_kw={"placeholder": "请输入文章标题"})
    submit = SubmitField('评 论')