"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/1 14:30
    file   : settings.py
"""

import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY','dev key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BLUELOG_POST_PER_PAGE = 10
    BLUELOG_MANAGE_POST_PER_PAGE = 15
    BLUELOG_COMMENT_PER_PAGE = 15

    SHARES_PER_PAGE = 5

    BLUELOG_EMAIL=os.getenv('BLUELOG_EMAIL')

    BLUELOG_THEMES={'perfect_blue': 'Perfect Blue',
                    'united': 'United',
                    'black_swan': 'Black Swan', }

    UPLOAD_PATH=os.path.join(basedir, 'uploads')
    AVATARS_SAVE_PATH=os.path.join(UPLOAD_PATH, 'avatars')
    AVATARS_SIZE_TUPLE=(30, 100, 200)

    PHOTO_SIZE={'small': 400, 'medium': 800}
    PHOTO_SUFFIX={
        PHOTO_SIZE['small']: '_s',
        PHOTO_SIZE['medium']: '_m',
    }
    PHOTO_PER_PAGE=20

    DROPZONE_ALLOWED_FILE_TYPE='image'
    DROPZONE_MAX_FILE_SIZE=3
    DROPZONE_MAX_FILES=30
    DROPZONE_ENABLE_CSRF=True
    DROPZONE_DEFAULT_MESSAGE='拖动图片至此处或点击选择图片开始上传'

    MAIL_SUBJECT_PREFIX='[test]'

    MAIL_SERVER='smtp.qq.com'
    MAIL_PORT=465
    MAIL_USE_SSL=True
    MAIL_USE_TSL=False
    MAIL_USERNAME='517584811@qq.com'
    MAIL_PASSWORD='kaercocatidebhfh'
    MAIL_DEFAULT_SENDER ='517584811@qq.com'

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir,'data-dev.db')
    # CACHE_TYPE='redis'
    # CACHE_REDIS_HOST='127.0.0.1'
    # CACHE_REDIS_PORT=6379
    # CACHE_REDIS_DB=''
    # CACHE_REDIS_PASSWORD=''

class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir,'data.db')

config = {
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig
}
