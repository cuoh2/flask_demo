"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/12 9:55
    file   : decorators.py
"""
from functools import wraps

from flask import flash
from flask_login import current_user

from app.utils import redirect_back


def admin_required(func):
    @wraps(func)
    def decorator(*args,**kwargs):
        if not current_user.is_admin:
            flash('无此权限','warning')
            return redirect_back()
        return func(*args,**kwargs)
    return decorator

def limit_user(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if current_user.is_limited:
            flash('无此权限', 'warning')
            return redirect_back()
        return func(*args, **kwargs)
    return decorator
