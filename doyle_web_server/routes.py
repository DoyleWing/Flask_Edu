'''实现与前端连接'''

import os  #找到路径
import secrets 
from  PIL import Image   #裁剪图片
from flask import Flask,render_template,url_for,flash,redirect, request,abort 
from doyle_web_server import app,db,bcrypt,mail
from doyle_web_server.forms import RegistrationForm,LoginForm,UpdateAccountForm,PostForm,RequestResetForm,ResetPasswordForm
from doyle_web_server.models import User, Post
from flask_login import login_user,current_user, logout_user, login_required
from flask_mail import Message

@app.route('/')
def index():
    page = request.args.get('page',1,type=int)   #设置每页的显示
    posts =Post.query.order_by(Post.date_posted.desc()).paginate(per_page=1)   #设置每页显示多少文章,order_by排序操作倒序排序，新发的提到前面
    return render_template("main.html",posts=posts)

@app.route('/about')
def about():
    return render_template("about.html",title="关于我们")

@app.route('/echo/<msg>')
def echo(msg):
    return '<h1>Hello I am a Echo Website I can echo everything:{}</h1>'.format(msg)

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data,email=form.email.data,password=hashed_password)
        #db.create_all() #首次使用
        db.session.add(user)
        db.session.commit()
        flash(f'您的账号已经成功注册了，欢迎【{form.username.data}】加入学习，加油继续学习','success')
        return redirect(url_for("login"))
    return render_template("register.html",title="注册界面", form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")

            flash(f'【{user.username}】您已成功登入，欢迎进入学习的天堂','succcess')
            return redirect(next_page) if next_page else redirect(url_for('index')) 
        else:
            flash("Oops,登录失败，再想想email和密码",'danger')
    
    return render_template("login.html",title="登录界面", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("index"))

def save_picture(form_picture): #储存图片
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_picture.filename)#返回名称和路径（默认default.jpg）
    picture_filename = random_hex + file_extension
    picture_path = os.path.join(app.root_path,"static/user_profile",picture_filename)#存储图片到指定路径
   #form_picture.save(picture_path)

    output_img_size = (100,100)
    thumbnail_img = Image.open(form_picture)
    thumbnail_img.thumbnail(output_img_size) #变成很小的image
    thumbnail_img.save(picture_path) #储存小图
    return picture_filename

@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("您的信息已经更新", 'success')
        return redirect(url_for('account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for("static",filename="user_profile/"+ current_user.image_file)  #导入图片
    return render_template("account.html",title="个人主页", image_file=image_file, form=form)

@app.route("/post/new", methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("您的文章已经成功发布", 'success')
        return redirect(url_for('index'))
    return render_template("create_post.html",title="写新的帖子" ,form=form, legend="发布文章")

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html",title=post.title,post=post)

@app.route("/post/<int:post_id>/update",methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()  #无需再add新的数据，直接提交
        flash("您已成功更新文章~",'success')
        return redirect(url_for("post" , post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template("create_post.html",title="更新文章", form=form, legend = "更新文章")


@app.route("/post/<int:post_id>/delete",methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('您的文章已经删除', 'success')
    return redirect(url_for('index'))

@app.route("/user/<string:username>")     #点击用户名跳转显示用户发布文章 
def user_posts(username):
    page = request.args.get('page',1,type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc())\
        .paginate(page=page,per_page=2)
    return render_template('user_posts.html',posts=posts,user=user)

def send_reset_email(user):   #发送邮件操作
    token= user.get_reset_token()
    msg = Message('关于重置账户信息的邮件',sender='doylewing@163.com',recipients=[user.email])
    msg.body = f'''请点击下列链接进行密码重置操作
{url_for('reset_token',token=token,_external=True)}
__________如果你没有进行重置操作却收到这封邮件，您的信息可能已被泄漏，请尽快修改密码________
'''
    mail.send(msg)

@app.route("/reset_password",methods = ['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("已经将重置密码邮件发发送到您的邮箱，请及时更改密码")
        return redirect(url_for('login'))
    return render_template('reset_request.html',title='重置密码页面',form=form)

@app.route("/reset_password/<token>",methods = ['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('不好意思，用户错误，请重新输入','warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash(f'您的密码已经成功修改，欢迎回到学习，加油继续学习','success')
        return redirect(url_for("login"))
    return render_template('reset_token.html',title='新密码页面',form=form)