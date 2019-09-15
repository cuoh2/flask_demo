"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/1 14:40
    file   : extensions.py
"""
from flask_bootstrap import Bootstrap
from flask_dropzone import Dropzone
from flask_login import LoginManager
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_avatars import Avatars
from flask_pagedown import PageDown
from flask_cache import Cache
from flask_mail import Mail
from flask_wtf import CSRFProtect
#from flask_socketio import SocketIO

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
avatars = Avatars()
dropzone = Dropzone()
pagedown = PageDown()
#cache = Cache()
mail = Mail()
moment = Moment()
csrf = CSRFProtect()
#socketio = SocketIO()

login_manager.login_view = 'web.login'
login_manager.login_message_category = 'warning'
login_manager.login_message='请先登录'
