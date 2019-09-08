"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/4 18:40
    file   : main.py
"""
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FileField, HiddenField
from wtforms.validators import DataRequired, Length, Regexp, Email, EqualTo, ValidationError, Optional
from wtforms.widgets import TextArea

from app.models import User


class NewpostForm():


   pass


class EditProfileForm(FlaskForm):
    username = StringField('用户名',validators=[DataRequired(message='请输入用户名'),Length(4,20),Regexp('^\w*$')])
    location = StringField('所在地',validators=[Optional(),Length(0,50)])
    bio = TextAreaField('简介',validators=[Optional(),Length(0,120)],widget=TextArea())
    submit = SubmitField('保存')

    def validate_username(self,field):
        if field.data != current_user.username and User.query.filter_by(
                            username=field.data).first():
            raise ValidationError('用户名已被使用')

class UploadAvatarForm(FlaskForm):
    image = FileField(validators=[
        FileRequired(),
        FileAllowed(['jpg','jpeg' 'png'], 'The file format should be .jpg or .png.')
    ])
    upload = SubmitField('上传预览')

class CropAvatarForm(FlaskForm):
    x=HiddenField()
    y=HiddenField()
    w=HiddenField()
    h=HiddenField()
    sumbmit=SubmitField('确认保存')