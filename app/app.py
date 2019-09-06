"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/6 19:23
    file   : app.py
"""
from datetime import date

from flask.json import JSONEncoder as _JSONEncoder
from flask import Flask as _Flask

class JSONEncoder(_JSONEncoder):
    def default(self, o):
        if hasattr(o,'keys') and hasattr(o,'__getitem__'):
            return dict(o)
        if isinstance(o,date):
            return o.strftime('%Y-%m-%d')

class Flask(_Flask):
    json_encoder = JSONEncoder