#coding:utf8
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired,ValidationError
from app.models import Admin

class LoginForm(FlaskForm):
    account=StringField(
        label="account",
        validators=[
            DataRequired("account empty")
        ],
        description="account name",
        render_kw={
            "class" :"form-control",
            "placeholder":"input account",
            # "required":"required"
        }
    )
    pwd=PasswordField(
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
    submit=SubmitField(
        label="login",
        render_kw={
            "class": "btn btn-primary btn-block btn-flat"
        }
    )

    def validate_account(self,field):
        account=field.data
        admin= Admin.query.filter_by(name=account).count()
        if admin==0:
            raise ValidationError("account not exist")
class TagForm(FlaskForm):
    name=StringField(
        label="name",
        validators=[
            DataRequired("Tag empty")
        ],
        description="Tag",
        render_kw={
            "class":"form-control",
            "id":"input_name",
            "placeholder":"请输入标签名称！"
        }
    )
    submit = SubmitField(
        label="add",
        render_kw={
            "class": "btn btn-primary"
        }
    )