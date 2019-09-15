"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/15 10:58
    file   : oauth.py
"""
from flask import Blueprint, abort, url_for, flash, redirect
from flask_login import current_user, login_user
from sqlalchemy import or_

from app import oauth, db
from app.models import User
from app.utils import redirect_back

oauth_bp = Blueprint('oauth',__name__)

github = oauth.remote_app(
    name='github',
    consumer_key='d931fee7f44f1d3977c1',
    consumer_secret='53ba0c7d5c423d062f8e38a05df27beb3f4cef25',
    request_token_params={'scope':'user'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)
providers={
    'github':github
}

@oauth_bp.route('/login/<provider_name>')
def oauth_login(provider_name):
    if current_user.is_authenticated:
        return redirect_back()
    provider = providers[provider_name]
    callback = url_for('.oauth_callback',provider_name=provider_name,_external=True)
    return provider.authorize(callback=callback)

@oauth_bp.route('/callback/<provider_name>')
def oauth_callback(provider_name):
    provider = providers[provider_name]
    response = provider.authorized_response()
    if response:
        access_token = response.get('access_token')
    else:
        access_token=None
        flash('连接失败，请重试','warning')
        return redirect(url_for('auth.login'))
    username, github, email, bio=get_social_profile(provider, access_token)
    user=User.query.filter(or_(User.username==username,User.email==email)).first()
    if not user:
        user=User(email=email, username=username, bio=bio)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('web.index'))
    login_user(user)
    return redirect(url_for('web.index'))

profile_endpoints={
    'github':'user',
}
def get_social_profile(provider,access_token):
    profile_endpoint = profile_endpoints[provider.name]
    response = provider.get(profile_endpoint,token=access_token)
    username=response.data.get('name')
    github=response.data.get('html_url')
    email=response.data.get('email')
    bio=response.data.get('bio')
    return username,github,email,bio
