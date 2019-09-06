"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/1 16:07
    file   : fake.py
"""

import random

import requests
import json
from time import sleep

from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Tag, User, Post, Comment
from faker import Faker
fake = Faker("zh_CN")

def fake_tag():
    '''填充tag'''
    tags = ['技术','生活','职场','资料','影音']
    for t in tags:
        tag = Tag(name=t)
        db.session.add(tag)
        db.session.commit()
    return 'Done'


def fake_users(num=10):
    '''填充用户'''
    for i in range(num):
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
                    member_since=fake.date_this_year()
                    )
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        print('已填充{}个用户'.format(i+1))
    return 'Done'

def fake_follows(count):
    for i in range(count):
        user = User.query.get(random.randint(1,User.query.count()))
        user.follow(User.query.get(random.randint(1,User.query.count())))
    db.session.commit()


def fake_post():
    '''填充帖子'''
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
            post.publish_time = fake.date_this_year()
            db.session.add(post)
            db.session.commit()
    return 'Done'

def fake_comment():
    for i in range(50):
        comment = Comment(
            content=fake.sentence(),
            publish_time=fake.date_this_year(),
            post=random.choice(Post.query.all()),
            author=random.choice(User.query.all())
        )
        db.session.add(comment)
        db.session.commit()
    return 'Done'



def fake_data():
    print('开始填充Tag')
    fake_tag()
    print('开始填充用户')
    fake_users(20)
    fake_follows(200)
    print('开始填充帖子')
    fake_post()
    print('开始填充评论')
    fake_comment()

