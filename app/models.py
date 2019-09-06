"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/1 14:30
    file   : models.py
"""
from datetime import datetime

from flask_avatars import Identicon
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text

from app import db, login_manager

class Follow(db.Model):
    """关注"""
    follower_id = Column(Integer,ForeignKey('users.id'),primary_key=True)
    follower = relationship('User',back_populates='following',foreign_keys=[follower_id],lazy='joined')
    """被关注"""
    followed_id = Column(Integer,ForeignKey('users.id'),primary_key=True)
    followed = relationship('User',back_populates='followers',foreign_keys=[followed_id],lazy='joined')
    timestamp = Column(DateTime,default=datetime.utcnow)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64),unique=True,index=True)
    bio=db.Column(db.String(120))
    location=db.Column(db.String(50))
    member_since=db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post',backref='author',lazy='dynamic')
    comments = db.relationship('Comment',backref='author',lazy='dynamic')
    collectags = db.relationship('CollecTag',backref='users',lazy='dynamic')
    collectposts = db.relationship('CollectPost',backref='users',lazy='dynamic')
    avatar_s=db.Column(db.String(64))
    avatar_m=db.Column(db.String(64))
    avatar_l=db.Column(db.String(64))
    avatar_raw=db.Column(db.String(64))
    following=db.relationship('Follow', back_populates='follower',
                              foreign_keys=[Follow.follower_id], lazy='dynamic', cascade='all')
    followers=db.relationship('Follow', back_populates='followed',
                              foreign_keys=[Follow.followed_id], lazy='dynamic', cascade='all')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.generate_avatar()
        self.follow(self)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def generate_avatar(self):
        avatar=Identicon()
        filenames=avatar.generate(text=self.username)
        self.avatar_s=filenames[0]
        self.avatar_m=filenames[1]
        self.avatar_l=filenames[2]
        db.session.commit()

    def reset_password(self,new_password):
        self.password = new_password
        db.session.commit()

    def follow(self,user):
        if not self.is_following(user):
            follow = Follow(follower=self,followed=user)
            db.session.add(follow)
            db.session.commit()

    def unfollow(self,user):
        follow = self.following.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()

    def is_following(self,user):
        if user.id is None:
            return False
        return self.following.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self,user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def keys(self):
        return ['id', 'email', 'username', 'location','bio']

    def __getitem__(self, item):
        return getattr(self,item)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    posts = db.relationship('Post',backref='tag',lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name
    def collection(self,user):
        return CollecTag.query.filter_by(tag_id=self.id,user_id=user.id).first()


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.Text)
    content = db.Column(db.Text)
    repies = db.Column(db.Integer,default=0)
    chick = db.Column(db.Integer,default=0)
    tag_id = db.Column(db.Integer,db.ForeignKey('tags.id'))
    publish_time = db.Column(db.DateTime,default=datetime.now())
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    comments = db.relationship('Comment',backref='post',lazy='dynamic')

    def chicking(self):
        self.chick = self.chick + 1
        db.session.add(self)
        db.session.commit()

    def collection(self,user):
        if not user.is_authenticated:
            return False
        return CollectPost.query.filter_by(post_id=self.id,user_id=user.id).first()

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.Text)
    publish_time = db.Column(db.DateTime,default=datetime.now())
    post_id = db.Column(db.Integer,db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))


class CollecTag(db.Model):
    __tablename__ = 'collactag'
    id = db.Column(db.Integer,primary_key=True)
    tag_id = db.Column(db.Integer,db.ForeignKey('tags.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    time = db.Column(db.DateTime,default=datetime.now())

class CollectPost(db.Model):
    __tablename__ = 'collectpost'
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    time = db.Column(db.DateTime, default=datetime.now())


