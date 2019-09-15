"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/1 14:26
    file   : __init__.py
"""
import os
from datetime import datetime

import click
from flask_login import current_user

from app.app import Flask
from app.settings import config
from app.extensions import bootstrap, db, login_manager, avatars, \
    dropzone, pagedown, mail, moment,csrf#,socketio
from fake import fake_data


def create_app(config_name=None):
    if not config_name:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask(__name__)

    app.config.from_object(config[config_name])
    register_commands(app)
    register_blueprint(app)
    register_extensions(app)
    register_shell_context(app)
    register_template_context(app)


    return app



def register_blueprint(app):
    from app.web import web
    from app.api import api
    from app.web.admin import admin
    app.register_blueprint(web)
    app.register_blueprint(api,url_prefix='/api')
    app.register_blueprint(admin,url_prefix='/admin')


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'web.login'
    login_manager.login_message_category = 'warning'
    avatars.init_app(app)
    pagedown.init_app(app)
    #cache.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    csrf.init_app(app)
    #socketio.init_app(app)


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        from app.models import Post,Message
        hot_posts=[p for p in Post.query.all() if (datetime.now() - p.publish_time).days == 0]
        hot_posts.sort(key=lambda x: x.comments.count(), reverse=True)
        if current_user.is_authenticated:
            message_count=Message.query.filter_by(user=current_user, is_read=False).count()
        else:
            message_count=None
        return {'hot_posts':hot_posts,'message_count':message_count}


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        from app.models import User, Tag, Post,Comment
        return dict(db=db, User=User, Post=Post, Tag=Tag,Comment=Comment)

def register_commands(app):
    @app.cli.command()
    @click.option('--drop',is_flag=True,help='Create tables after drop')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, '
                          'do you want to continue?',abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    def forge():
        """Generate fake data."""
        #db.drop_all()
        db.create_all()
        #fake_data()
        click.echo('Done.')


