"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/4 15:52
    file   : utils.py
"""
from urllib.parse import urlparse, urljoin

from flask import current_app, request, redirect, url_for
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature

def get_token(user,expiration=3600):
    s = Serializer(current_app.config['SECRET_KEY'],expiration)
    token = s.dumps({'id':user.id}).decode('utf-8')
    return token

def validate_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except(SignatureExpired,BadSignature):
        return False
    user_id = data['id']
    return user_id


def is_safe_url(url):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url,url))
    return test_url.scheme in ['http','https'] \
           and test_url.netloc == ref_url.netloc


def redirect_back(default='web.index',**kwargs):
    for target in request.args.get('next'),request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default,**kwargs))

ALLOWED_EXTENSIONS=['png','jpg','jpeg','gif']

def is_allowed_type(filename):
    return '.' in filename and filename.rsplit('.',1)[-1] in ALLOWED_EXTENSIONS