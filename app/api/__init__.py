"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/6 19:17
    file   : __init__.py.py
"""
from flask import Blueprint

api = Blueprint('api',__name__)

from . import user,main