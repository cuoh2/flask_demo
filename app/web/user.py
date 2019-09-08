"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/5 14:04
    file   : user.py
"""
import os

from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db, avatars
from app.forms.main import EditProfileForm, UploadAvatarForm, CropAvatarForm
from app.utils import redirect_back, is_allowed_type
from . import web
from app.models import User, Tag, Post, Collect, Comment
from flask import render_template, request, url_for, redirect, flash, make_response, jsonify, current_app

@web.route('/member/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    per_page=current_app.config['POST_PER_PAGE']
    page=request.args.get('page', type=int, default=1)
    tags = Tag.query.order_by(Tag.id).all()
    tag = request.args.get('tag', 'all')
    t = Tag.query.filter_by(name=tag).first()
    if tag == 'all':
        pagination=Post.query.filter_by(author_id=user.id).order_by(
                        Post.publish_time.desc()).paginate(page, per_page)
    else:
        pagination=Post.query.filter_by(tag_id=t.id,author_id=user.id).order_by(
                        Post.publish_time.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('user.html', tags=tags, tag=tag, pagination=pagination,posts=posts, user=user)

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

@web.route('/collects/<int:user_id>')
@login_required
def show_collects(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.join(Collect, Collect.post_id == Post.id).filter(Collect.user_id==current_user.id).all()
    return render_template('user_collect_posts.html',posts=posts,user=user)


@web.route('/settings/profile/<int:user_id>',methods=['GET','POST'])
@login_required
def edit_profile(user_id):
    user = User.query.get_or_404(user_id)
    if current_user != user:
        return False
    form = EditProfileForm()
    upload_form=UploadAvatarForm()
    crop_form=CropAvatarForm()
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
    return render_template('user_edit_profile.html',user=user,form1=form, upload_form=upload_form, crop_form=crop_form)
#
# @web.route('/settings/avatar/<int:user_id>',methods=['GET','POST'])
# @login_required
# def change_avatar(user_id):
#     user = User.query.get_or_404(user_id)
#     if request.method == 'POST':
#         file = request.files['file']
#         if file and is_allowed_type(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(current_app.config['UPLOAD_PATH'],filename))
#             flash('上传成功')
#             return
#         flash('请上传正确的文件的类型')
#     return redirect(url_for('.edit_profile',user_id=user.id))

@web.route('/settings/avatar/<int:user_id>')
@login_required
def change_avatar(user_id):
    user=User.query.get_or_404(user_id)
    return redirect(url_for('.edit_profile',user_id=user.id))

@web.route('/settings/avatar/<int:user_id>/upload',methods=['POST'])
@login_required
def upload_avatar(user_id):
    user=User.query.get_or_404(user_id)
    form = UploadAvatarForm()
    if form.validate_on_submit():
        image = form.image.data
        filename = avatars.save_avatar(image)
        current_user.avatar_raw = filename
        db.session.commit()
    return redirect(url_for('.change_avatar',user_id=user.id))

@web.route('/settings/avatar/<int:user_id>/crop',methods=['POST'])
@login_required
def crop_avatar(user_id):
    user=User.query.get_or_404(user_id)
    form = CropAvatarForm()
    if form.validate_on_submit():
        x = form.x.data
        y = form.y.data
        w = form.w.data
        h = form.h.data
        filename = avatars.crop_avatar(current_user.avatar_raw,x,y,w,h)
        current_user.avatar_s = filename[0]
        current_user.avatar_m = filename[1]
        current_user.avatar_l = filename[2]
        db.session.commit()
        flash('头像保存成功', 'success')
    return redirect(url_for('.change_avatar',user_id=user.id))
