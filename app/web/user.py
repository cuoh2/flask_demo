"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/5 14:04
    file   : user.py
"""
from flask_login import login_required, current_user

from app import db
from app.forms.main import EditProfileForm
from app.utils import redirect_back
from . import web
from app.models import User, Tag, Post
from flask import render_template, request, url_for, redirect, flash, make_response, jsonify, current_app

@web.route('/member/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    tags = Tag.query.order_by(Tag.id).all()
    tag = request.args.get('tag', 'all')
    t = Tag.query.filter_by(name=tag).first()
    if tag == 'all':
        posts=Post.query.filter_by(author_id=user.id).all()
    else:
        posts=Post.query.filter_by(
            tag_id=t.id,author_id=user.id).order_by(Post.publish_time.desc()).all()
        posts.sort(key=lambda x: x.comments.count(), reverse=True)
    return render_template('user.html', tags=tags, tag=tag, posts=posts, user=user)

@web.route('/member/<int:user_id>/followings')
def show_followings(user_id):
    user = User.query.get_or_404(user_id)
    followings = user.following.all()
    followed_ids = [user.followed_id for user in followings]
    followed_ids.remove(user_id)
    followings = [User.query.get_or_404(id) for id in followed_ids]
    return render_template('user_followings.html',friends=followings,user=user)

@web.route('/member/<int:user_id>/fans')
def show_fans(user_id):
    user=User.query.get_or_404(user_id)
    fans=user.followers.all()
    follower_ids=[user.follower_id for user in fans]
    follower_ids.remove(user_id)
    fans = [User.query.get_or_404(id) for id in follower_ids]
    return render_template('user_followers.html',friends=fans,user=user)


@web.route('/follow/<int:user_id>',methods=['POST'])
@login_required
def follow(user_id):
    user = User.query.get_or_404(user_id)
    if not current_user.is_following(user):
        current_user.follow(user)
    return redirect_back()

@web.route('/unfollow/<int:user_id>',methods=['POST'])
@login_required
def unfollow(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.is_following(user):
        current_user.unfollow(user)
    return redirect_back()

@web.route('/settings/profile/<int:user_id>',methods=['GET','POST'])
@login_required
def edit_profile(user_id):
    user = User.query.get_or_404(user_id)
    form = EditProfileForm()
    if form.validate_on_submit():
        user.username = form.username.data
        user.location = form.location.data
        user.bio = form.bio.data
        db.session.commit()
        flash('请输入正确信息','warning')
        return redirect(url_for('web.user',username=user.username))
    form.username.data = user.username
    form.location.data = user.location
    form.bio.data = user.bio
    return render_template('user_edit_profile.html',user=user,form=form)