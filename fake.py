"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/1 16:07
    file   : fake.py
"""

import random
import threading
import time

import requests
import json
from time import sleep

from flask import current_app
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Tag, User, Post, Comment, Collect, Role
from faker import Faker
fake = Faker("zh_CN")

def fake_tag():
    tags = ['技术','生活','职场','资料','影音']
    for t in tags:
        tag = Tag(name=t)
        db.session.add(tag)
        db.session.commit()
    return 'Done'

def init_role():
    role_name = ['超级管理员','管理员','用户','限制用户']
    for id,name in enumerate(role_name,1):
        role = Role(id=id,name=name)
        db.session.add(role)
    db.session.commit()

def fake_admin():
    user=User(username='admin',
              password='qqqqqq',
              email='517584811@qq.com',
              location='SZ',
              bio=fake.sentence(),
              member_since=fake.date_this_year(),
              role_id=1,
              )
    db.session.add(user)
    db.session.commit()
    return 'Done'

def fake_moderators(count):
    for i in range(count):
        url = 'https://randomuser.me/api/'
        r = requests.get(url).text
        data = json.loads(r)
        username = data['results'][0]['login']['username']
        password = data['results'][0]['login']['password']
        email = data['results'][0]['email']
        location = data['results'][0]['location']['city']
        user = User(username=username,
                    password=password,
                    email=email,
                    location=location,
                    bio=fake.sentence(),
                    member_since=fake.date_this_year(),
                    role_id=2
                    )
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
    return 'Done'


def fake_users(count):
    for i in range(count):
        url = 'https://randomuser.me/api/'
        r = requests.get(url).text
        data = json.loads(r)
        username = data['results'][0]['login']['username']
        password = data['results'][0]['login']['password']
        email = data['results'][0]['email']
        location = data['results'][0]['location']['city']
        user = User(username=username,
                    password=password,
                    email=email,
                    location=location,
                    bio=fake.sentence(),
                    member_since=fake.date_this_year(),
                    role_id=3
                    )
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
    return 'Done'

def fake_follows(count):
    for i in range(count):
        user = User.query.get(random.randint(1,User.query.count()))
        user.follow(User.query.get(random.randint(1,User.query.count())))
    db.session.commit()


def fake_post(count):
    for i in range(count):
        url = "https://www.v2ex.com/api/topics/latest.json"
        r = requests.get(url).text
        datas = json.loads(r)
        for data in datas:
            title = data['title']
            content = data['content_rendered']
            if title:
                post = Post(title=title,content=content)
                post.tag = Tag.query.get(random.randint(1, Tag.query.count()))
                post.author = random.choice(User.query.all())
                post.publish_time = fake.date_time_between(start_date="-1d", end_date="now", tzinfo=None)
                #post.publish_time = fake.date_time_this_year()
                db.session.add(post)
                db.session.commit()
    return 'Done'

def fake_comment(count):
    for i in range(count):
        comment = Comment(
            content=fake.sentence(),
            publish_time=fake.date_this_year(),
            post=random.choice(Post.query.all()),
            author=random.choice(User.query.all())
        )
        db.session.add(comment)
        db.session.commit()
    return 'Done'

def fake_collect(count):
    for i in range(count):
        collect = Collect(
            user=random.choice(User.query.all()),
            #user=User.query.get(31),
            post=random.choice(Post.query.all()),
            time=fake.date_this_year()
        )
        db.session.add(collect)
        db.session.commit()
    return 'Done'



def async_fake_user(app,count):
    with app.app_context():
        fake_moderators(2)
        fake_users(count)

def fake_data():
    # print('开始填充Tag...')
    # fake_tag()
    # init_role()
    # print('开始填充管理员...')
    # fake_admin()
    # print('开始填充用户...')
    # t1=time.time()
    # app=current_app._get_current_object()
    # thr=[]
    # for i in range(3):
    #     t = threading.Thread(target=async_fake_user,args=(app,10))
    #     thr.append(t)
    #
    # for t in thr:
    #     t.start()
    #     print(t.name+'正在进行...')
    #
    # for t in thr:
    #     t.join()
    # t2=time.time()
    # print(t2-t1)
    #
    # print('开始填充关注...')
    # fake_follows(50)

    # print('开始填充帖子...')
    # fake_post(2)

    print('开始填充评论...')
    fake_comment(1000)

    # print('开始填充收藏...')
    # fake_collect(20)
