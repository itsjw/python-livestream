#coding:utf8
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired,EqualTo,Email,Regexp

class UserForm(FlaskForm):
    name = StringField(
        label="account",
        validators=[
            DataRequired("account empty")
        ],
        description="account name",
        render_kw={
            "class": "form-control",
            "placeholder": "input account",
            # "required":"required"
        }
    )
    email=StringField(
        label="email",
        validators=[
            DataRequired("email empty"),
            Email("email format wrong")
        ],
        description="email",
        render_kw={
            "class": "form-control",
            "placeholder": "input email",
            # "required":"required"
        }
    )
    phone=StringField(
        label="phone",
        validators=[
            DataRequired("phone empty"),
            Regexp("\d{10}",message="phone format wrong")
        ],
        description="phone",
        render_kw={
            "class": "form-control",
            "placeholder": "input phone",
            # "required":"required"
        }
    )
    pwd = PasswordField(
        label="password",
        validators=[
            DataRequired("password empty")
        ],
        description="password",
        render_kw={
            "class": "form-control",
            "placeholder": "input password",
            # "required": "required"
        }
    )
    r_pwd = PasswordField(
        label="password",
        validators=[
            DataRequired("password empty"),
            EqualTo('pwd',message="password not same")
        ],
        description="password",
        render_kw={
            "class": "form-control",
            "placeholder": "input password",
            # "required": "required"
        }
    )
    submit = SubmitField(
        label="signup",
        render_kw={
            "class": "btn btn-primary btn-block btn-flat"
        }
    )
class UserForm(FlaskForm):
    name = StringField(
        label="account",
        validators=[
            DataRequired("account empty")
        ],
        description="account name",
        render_kw={
            "class": "form-control",
            "placeholder": "input account",
            # "required":"required"
        }
    )
    email = StringField(
        label="email",
        validators=[
            DataRequired("email empty"),
            Email("email format wrong")
        ],
        description="email",
        render_kw={
            "class": "form-control",
            "placeholder": "input email",
            # "required":"required"
        }
    )
    phone = StringField(
        label="phone",
        validators=[
            DataRequired("phone empty"),
            Regexp("\d{10}", message="phone format wrong")
        ],
        description="phone",
        render_kw={
            "class": "form-control",
            "placeholder": "input phone",
            # "required":"required"
        }
    )
    face=FileField(

    )
    submit = SubmitField(
        label="signup",
        render_kw={
            "class": "btn btn-primary btn-block btn-flat"
        }
    )