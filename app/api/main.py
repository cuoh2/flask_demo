"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/7 18:03
    file   : main.py
"""
from flask import jsonify, session
from sqlalchemy import func


from app.models import Post, Comment
from . import api


@api.route('/post/<post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify(post)

@api.route('/posts')
def posts():
    #posts = Post.query.order_by(Post.id).all()
    posts =Post.query.join(Comment).group_by(Post.id).order_by(
             func.count(Comment.id).desc()).all()
    return jsonify(posts)

@api.route('/comments')
def comments():
    comments = Comment.query.all()
    comments = Comment.query().order_by(func.count(Comment.post_id)).limit(20)
    return jsonify(comments)
