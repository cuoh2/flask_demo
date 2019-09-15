"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/1 14:29
    file   : auth.py
"""
from flask import request, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, login_required

from app.email import send_mail
from app.models import User
from app.utils import get_token, validate_token
from .. import db
from app.forms.auth import RegisterForm, LoginForm, Forget_passwordForm, Reset_passwordForm
from . import web


@web.route('/register',methods=['POST','GET'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User(username=form.username.data,email=form.email.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功！请登录', 'success')
        login_user(user)
        return redirect(url_for('web.index'))
    return render_template('user_register.html',form=form)

@web.route('/login',methods=['POST','GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user.password_hash:
            flash('该账号为第三方登录账号，请重新登录', 'warning')
            return redirect(url_for('.login'))
        if user and user.verify_password(form.password.data):
            login_user(user)
            return redirect(request.args.get('next') or url_for('web.index'))
        flash('密码错误','warning')
    return render_template('user_login.html',form=form)

@web.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('web.index'))

@web.route('/forget_password',methods=['POST','GET'])
def forget_password():
    form = Forget_passwordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if send_mail(form.email.data,'用户密码找回',
                'forget_password_email.html',user=user, token=get_token(user)):
            return
        flash('找回密码的邮件已经发送到' + form.email.data + ',请及时查收！','info')
    return render_template('forget_password.html', form=form)

@web.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
    form=Reset_passwordForm()
    if form.validate_on_submit():
        user_id=validate_token(token)
        if user_id:
            user=User.query.get(user_id)
            user.reset_password(form.password2.data)
            flash('密码已更新,请使用新密码登录', 'success')
            return redirect(url_for('.login'))
    return render_template('reset_password.html', form=form)