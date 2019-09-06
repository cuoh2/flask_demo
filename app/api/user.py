"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/6 19:17
    file   : user.py
"""
from flask import jsonify

from app.models import User
from . import api


@api.route('/user/<user_id>')
def user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user)