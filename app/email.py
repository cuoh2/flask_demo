"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/4 16:30
    file   : email.py
"""
from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from app import mail


def send_async_mail(app,msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            raise e

def send_mail(to,subject,template,**kwargs):
    message = Message(current_app.config['MAIL_SUBJECT_PREFIX'] + subject, recipients=[to])
    message.html = render_template(template, **kwargs)
    app = current_app._get_current_object()
    thr = Thread(target=send_async_mail,args=[app,message])
    thr.start()
