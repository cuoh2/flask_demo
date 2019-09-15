"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/8 14:10
    file   : admin.py
"""
from datetime import datetime

from flask import Blueprint

from flask import render_template, request, url_for, redirect, \
    flash, make_response, jsonify, current_app
from flask_login import current_user, login_required
#from flask_socketio import emit
from sqlalchemy import func, or_

from app import db#, socketio
from app.decorators import admin_required

from app.models import User, Post, Role, Comment
from app.utils import redirect_back

admin = Blueprint('admin',__name__)

@admin.route('/')
@login_required
@admin_required
def index():
    user_count = User.query.count()
    users = User.query.all()
    new_user = 0
    for user in users:
        if user.member_since.date() == datetime.now().date():
            new_user+=1

    post_count=Post.query.count()
    posts = Post.query.all()
    new_posts = 0
    for post in posts:
        if post.publish_time.date() == datetime.now().date():
            new_posts +=1
    return render_template('admin/index.html',post_count=post_count,user_count=user_count,
                           new_user=new_user,new_posts=new_posts,user=current_user,info='index')

@admin.route('/users')
@login_required
@admin_required
def users():
    per_page=current_app.config['POST_PER_PAGE']
    page=request.args.get('page', type=int, default=1)
    rule = request.args.get('rule','all')
    if request.args.get('word'):
        word = request.args.get('word')
        word='%' + word.strip() + '%'
        pagination=User.query.filter(User.username.like(word)).paginate(page,per_page)
    elif rule =='new':
        pagination = User.query.order_by(User.member_since.desc()).paginate(page,per_page)
    elif rule == 'moderators':
        pagination = User.query.filter(or_(User.role_id==1,User.role_id==2)).paginate(page,per_page)
    elif rule == 'sum':
        pagination = User.query.join(Post,isouter=True).group_by(User.id).order_by(
            func.count(Post.id).desc()).paginate(page,per_page)
    else:
        pagination=User.query.paginate(page, per_page)
    users=pagination.items
    roles = Role.query.filter(Role.id !=1).all()
    roles2 = Role.query.filter(Role.id !=1,Role.id !=2).all()
    return render_template('admin/users.html',users=users,pagination=pagination,
                           user=current_user,roles=roles,roles2=roles2,info='users')

@admin.route('/posts',methods=['GET','POST'])
@login_required
@admin_required
def posts():
    per_page=current_app.config['POST_PER_PAGE']
    page=request.args.get('page', type=int, default=1)
    rule=request.args.get('rule', 'all')
    if request.args.get('word'):
        word = request.args.get('word')
        word = '%' + word.strip() + '%'
        pagination=Post.query.join(User).filter(or_(Post.title.like(word), User.username.like(word))).order_by(
            Post.publish_time.desc()).paginate(page, per_page)
    elif rule =='hot':
        pagination=Post.query.join(Comment).group_by(Post.id).order_by(
                    func.count(Comment.id).desc(), Comment.publish_time).paginate(page, per_page)
    else:
        pagination=Post.query.order_by(Post.publish_time.desc()).paginate(page, per_page)
    posts=pagination.items
    return render_template('admin/posts.html',posts=posts,pagination=pagination,user=current_user,info='posts')

@admin.route('/posts/delete',methods=['GET','POST'])
@login_required
@admin_required
def delete_post():
    ids = request.form.getlist('id_list')
    for id in ids:
        post = Post.query.get_or_404(id)
        db.session.delete(post)
        db.session.commit()
    return redirect_back()

@admin.route('/user/role',methods=['GET','POST'])
@login_required
@admin_required
def set_role():
    user_id = request.form.get('user_id')
    user = User.query.get(user_id)
    role_id = request.form.get('new_role_id')
    user.role_id = role_id
    db.session.commit()
    return redirect_back()


# online_users=[]
#
# @socketio.on('connect')
# def connect():
#     global online_users
#     if current_user.is_authenticated and current_user.id not in online_users:
#         online_users.append(current_user.id)
#     emit('user count',{'count':len(online_users)},broadcast=True)
#
# @socketio.on('disconnect')
# def disconnect():
#     global online_users
#     if current_user.is_authenticated and current_user.id in online_users:
#         online_users.remove(current_user.id)
#     emit('user count',{'count':len(online_users)},broadcast=True)
