"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/1 14:29
    file   : __init__.py.py
"""
from flask import Blueprint

web = Blueprint('web',__name__)

from . import auth,main,user
