'''完成需要执行操作的代码需求,数据导入'''

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed 
#上传文件，以及文件类型
from flask_login import current_user
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextAreaField
from wtforms.validators import DataRequired, Length,Email,EqualTo,ValidationError
#导入validators 用于校验数据，长度，email，EqualTo校验前后数据
from doyle_web_server.models import User

class RegistrationForm(FlaskForm):
    username = StringField("昵称",validators=[DataRequired(message="必填请输入"),Length(min=2,max=20,message="名称至少要2-20字符")])
    email = StringField("邮箱",validators=[DataRequired(message="必填请输入"),Email(message="别闹，请正确输入")])  #一定要校验数据
    password = PasswordField("密码",validators=[DataRequired(message="必填请输入")])
    confirm_password = PasswordField("确认密码",validators=[DataRequired(message="需验证请输入原密码"),EqualTo("password",message="两次输入不一样")])
    submit = SubmitField("注 册") #提交数据

    def validate_username(self,username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError("不好意思，这个用户名已经有人注册")
    def validate_email(self,email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError("不好意思，这个邮箱已经有人注册")

class UpdateAccountForm(FlaskForm):
    username = StringField("昵称",validators=[DataRequired(message="必填请输入"),Length(min=2,max=20,message="名称至少要2-20字符")])
    email = StringField("邮箱",validators=[DataRequired(message="必填请输入"),Email(message="别闹，请正确输入")])  #一定要校验数据
    submit = SubmitField("更新个人信息") #提交数据
    picture = FileField("更改头像",validators=[FileAllowed(["jpg","png"],message="只支持上传jpg和png格式图片")])

    def validate_username(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError("不好意思，这个用户名已经有人注册")
    def validate_email(self,email):
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError("不好意思，这个邮箱已经有人注册")

class LoginForm(FlaskForm):
    email = StringField("邮箱",validators=[DataRequired(message="必填请输入"),Email()])  #一定要校验数据
    password = PasswordField("密码",validators=[DataRequired(message="必填请输入")])
    remember = BooleanField("记住密码")
    submit = SubmitField("登 录") #提交数据

class PostForm(FlaskForm):
    title = StringField("文章标题", validators=[DataRequired(message="不能发空文章")])
    content = TextAreaField("文章内容",validators=[DataRequired(message="不能发空内容")])
    submit = SubmitField("提交")

class RequestResetForm(FlaskForm):#完成reset操作
    email = StringField("邮箱",validators=[DataRequired(message="必填请输入"),Email(message="别闹，请正确输入")])
    submit = SubmitField("点我找回密码")
    def validate_email(self,email):
        user =User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("邮箱输入错误")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("原始密码",validators=[DataRequired(message="必填请输入")])
    confirm_password = PasswordField("确认密码",validators=[DataRequired(message="需验证请输入原密码"),EqualTo("password",message="两次输入不一样")])
    submit = SubmitField("重置密码")