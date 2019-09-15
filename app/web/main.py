"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/1 14:29
    file   : web.py
"""
import re

from flask_socketio import emit
from sqlalchemy import func, or_

from app.decorators import limit_user
from . import web
from flask import render_template, request, url_for, redirect, flash, make_response, jsonify, send_from_directory, \
    current_app, Response
from ..models import Tag, Post, User, Comment, Collect, Message
from .. import db,socketio#, cache
from flask_login import login_required, current_user
from datetime import datetime,date
from markdown import markdown
import bleach
import json



@web.route('/')
# @cache.cached(timeout=60*2)
def index():
    per_page = current_app.config['POST_PER_PAGE']
    page = request.args.get('page',type=int,default=1)
    tags = Tag.query.order_by(Tag.id).all()
    tag = request.args.get('tag','')
    if tag and tag != request.cookies.get('tag',''):
        index_cookie(tag)
    else:
        tag = request.cookies.get('tag','all')
    t = Tag.query.filter_by(name=tag).first()

    if tag == 'all':
        pagination = Post.query.join(Comment,isouter=True).group_by(Post.id).order_by(
              Post.publish_time.desc(),Comment.publish_time.desc()).paginate(page,per_page)
    elif tag == 'hot':
        pagination = Post.query.join(Comment).group_by(Post.id).order_by(
             func.count(Comment.id).desc(),Comment.publish_time).paginate(page,per_page)
    else:
        pagination = Post.query.filter_by(tag_id=t.id).join(Comment).group_by(Post.id).order_by(
              Post.publish_time.desc(),Comment.publish_time.desc()).paginate(page,per_page)
    posts = pagination.items
    return render_template('index.html',tags=tags,tag=tag,posts=posts,pagination=pagination,user=current_user)

def index_cookie(tag):
    resp = make_response(redirect(url_for('web.index',tag=tag)))
    resp.set_cookie('tag',tag,max_age=24*60*60)
    return resp


@web.route('/search')
def search():
    word = request.args.get('word')
    word='%'+word.strip()+'%'
    posts=Post.query.join(User).filter(or_(Post.title.like(word))).order_by(
        Post.publish_time.desc()).all()
    search_user = User.query.filter(User.username.like(word)).all()
    return render_template('search.html',posts=posts,search_user=search_user,user=current_user)

def content_clean(c):
    exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite', 'markdown.extensions.tables',
            'markdown.extensions.toc']
    allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                    'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                    'h1', 'h2', 'h3', 'p','img','figure']
    content = bleach.linkify(bleach.clean(
        markdown(c, output_format='html5',extensions=exts),
        tags=allowed_tags, strip=True))
    return content

def title_clean(t):
    allowed_tags = []
    title = bleach.linkify(bleach.clean(
        markdown(t, output_format='html'),
        tags=allowed_tags, strip=True))
    return title


@web.route('/p/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    post.clicking()
    comments = post.comments.all()
    last_comment = post.last_comment
    return render_template('post.html',post=post,comments=comments,last_comment=last_comment,user=current_user)

@web.route('/p/<int:id>/reply',methods=['POST'])
@login_required
@limit_user
def new_comment(id):
    post = Post.query.get_or_404(id)
    if request.method == 'POST':
        content = request.form.get('comment-content','')
        if not content:
            return redirect(url_for('web.post', id=post.id))
        username = re.match('@(.*)\s',content)
        if username:
            name = username.group(1)
            user = User.query.filter_by(username=name).first()
            if user:
                content = content.replace(name,'<a href="/member/%s">%s</a>' %(name,name))
                if user != current_user:
                    message = Message(user_id=user.id,
                                      content='<a href="{}">{}</a><a href="{}#comments">在评论里提到了你</a>'.format(
                                          url_for('web.user', username=user.username),user.username,url_for(
                                              'web.post',id=id)))
                    db.session.add(message)
        comment = Comment(user_id=current_user.id,post_id=post.id,content=content_clean(content))
        if current_user != post.author:
            message = Message(user_id=post.author.id,
                              content='<a href="{}">{}</a><a href="{}#comments">评论了你的帖子</a>'.format(
                                  url_for('web.user', username=current_user.username), current_user.username,
                                  url_for('web.post', id=id)))
            db.session.add(message)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('web.post',id=post.id))

@web.route('/new',methods=['GET','POST'])
#@cache.cached(timeout=60*2)
@login_required
@limit_user
def new_post():
    tags = Tag.query.all()
    hot_tags = sorted(tags,key=lambda x: x.posts.count(),reverse=True)[:3]
    if request.method == 'POST':
        title =request.form.get('title')
        content = request.form.get('content')
        tag_id = request.form.get('tag_id')
        p = Post(title=title_clean(title),content=content_clean(content),tag_id=int(tag_id),author_id=current_user.id)
        db.session.add(p)
        db.session.commit()
        return jsonify({'result':'ok'})
    return render_template('new_post.html',tags=tags,hot_tags=hot_tags)

@web.route('/view/post')
@login_required
def view_post():
    content = request.args.get('content','')
    return content_clean(content)

@web.route('/collect/post')
@login_required
def collect_post():
    if not current_user.is_authenticated:
        return False
    post_id = request.args.get('post_id')
    post = Post.query.filter_by(id=post_id).first()
    if post:
        c = Collect.query.filter_by(post_id=post_id,user_id=current_user.id).first()
        if c:
            db.session.delete(c)
            db.session.commit()
            return {
                     "res": '加入收藏',
                    "count":current_user.collections.count()
                }
        else:
            c = Collect(post_id=post_id, user_id=current_user.id)
            db.session.add(c)
            db.session.commit()
            return Response(json.dumps({"res": '取消收藏',
                                        "count": current_user.collections.count()
                                        }))

    return {"res": '加入收藏' }


@web.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'],filename)

@web.route('/delete/<int:post_id>',methods=['GET','POST'])
@login_required
def delete_post(post_id):
    if request.method == 'POST':
        post = Post.query.get_or_404(post_id)
        if post:
            db.session.delete(post)
            db.session.commit()
            return redirect(url_for('.user',username=current_user.username))

@web.route('/edit/post/<int:post_id>',methods=['GET','POST'])
@login_required
def edit_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    tags=Tag.query.all()
    hot_tags=sorted(tags, key=lambda x: x.posts.count(), reverse=True)[:3]
    if request.method == 'POST':
        title =request.form.get('title')
        content = request.form.get('content')
        tag_id = request.form.get('tag_id')
        post.title=title_clean(title)
        post.content=content_clean(content)
        post.tag_id=int(tag_id)
        db.session.commit()
        return jsonify({'result':'ok','post_id':post.id})
    return render_template('post_edit.html',tags=tags,hot_tags=hot_tags,post=post)

@web.route('/<int:user_id>/message')
@login_required
def read_message(user_id):
    messages = Message.query.filter_by(user_id=user_id).order_by(Message.time.desc()).all()
    for message in messages:
        message.is_read = True
    db.session.commit()
    return render_template('user_read_messages.html',messages=messages,user=current_user)


@web.route('/message_count')
@login_required
def messages_count():
    count=Message.query.filter_by(user=current_user, is_read=False).count()
    return jsonify(count=count)

online_users=[]
@socketio.on('connect',namespace='/admin')
def connect():
    global online_users
    if current_user.is_authenticated and current_user.id not in online_users:
        online_users.append(current_user.id)
    emit('user online',{'count':len(online_users)},broadcast=True)

@socketio.on('disconnect',namespace='/admin')
def disconnect():
    global online_users
    if current_user.is_authenticated and current_user.id in online_users:
        online_users.remove(current_user.id)
    emit('user online',{'count':len(online_users)},broadcast=True)
