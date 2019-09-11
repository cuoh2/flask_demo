"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/6 19:17
    file   : user.py
"""
from flask import jsonify
from sqlalchemy import func

from app import db
from app.models import User, Role, Post
from . import api


@api.route('/user/<user_id>')
def user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user)

@api.route('/users')
def users():
    #users = User.query.all()
    users=db.session.query(User).outerjoin(Post,Post.author_id==User.id).group_by(User.id).order_by(
        func.count(Post.id).desc()).all()


    return jsonify(users)

@api.route('/roles')
def role_map():
    role = Role.query.all()
    return jsonify(role)