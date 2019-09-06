"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/4 18:40
    file   : main.py
"""
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp, Email, EqualTo, ValidationError, Optional
from wtforms.widgets import TextArea

from app.models import User


class NewpostForm():


   pass


class EditProfileForm(FlaskForm):
    username = StringField('用户名',validators=[DataRequired(),Length(4,20),Regexp('^\w*$')])
    location = StringField('所在地',validators=[Optional(),Length(0,50)])
    bio = TextAreaField('简介',validators=[Optional(),Length(0,120)],widget=TextArea())
    submit = SubmitField('修改')

    def validate_username(self,field):
        if field.data != current_user.username and User.query.filter_by(
                            username=field.data).first():
            raise ValidationError('用户名已被使用')