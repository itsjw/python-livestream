#coding:utf8
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,FileField,TextAreaField,SelectField,SelectMultipleField
from wtforms.validators import DataRequired,ValidationError
from app.models import Admin,Tag,Auth,Role

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
            "placeholder":"please input tag！"
        }
    )
    submit = SubmitField(
        label="add",
        render_kw={
            "class": "btn btn-primary"
        }
    )
class MovieForm(FlaskForm):
    tags = Tag.query.all()
    title = StringField(
        label="title",
        validators=[
            DataRequired("title empty")
        ],
        description="title",
        render_kw={
            "class": "form-control",
            "id": "input_title",
            "placeholder": "please input title！"
        }
    )
    url=FileField(
        label="file",
        validators=[
            DataRequired("please upload file！")
        ],
        description="file"
    )
    info = TextAreaField(
        label="info",
        validators=[
            DataRequired("info empty")
        ],
        description="info",
        render_kw={
            "class": "form-control",
            "rows":10
        }
    )
    logo = FileField(
        label="logo",
        validators=[
            DataRequired("please upload logo！")
        ],
        description="logo"
    )
    star=SelectField(
        label="star",
        validators=[
            DataRequired("please select star！")
        ],
        description="star",
        coerce=int,
        choices=[(1,"1 star"),(2,"2 star"),(3,"3 star"),(4,"4 star"),(5,"5 star")],
        render_kw={
            "class": "form-control",
        }
    )
    tag_id = SelectField(
        label="tag_id",
        validators=[
            DataRequired("please select tag_id！")
        ],
        description="tag_id",
        coerce=int,
        choices=[(i.id,i.name) for i in tags],
        render_kw={
            "class": "form-control",
        }
    )
    area = StringField(
        label="area",
        validators=[
            DataRequired("area empty")
        ],
        description="area",
        render_kw={
            "class": "form-control",
            # "id": "input_area",
            "placeholder": "please input area！"
        }
    )
    length = StringField(
        label="length",
        validators=[
            DataRequired("length empty")
        ],
        description="length",
        render_kw={
            "class": "form-control",
            # "id": "input_length",
            "placeholder": "please input length！"
        }
    )
    release_time= StringField(
        label="release_time",
        validators=[
            DataRequired("release_time empty")
        ],
        description="release_time",
        render_kw={
            "class": "form-control",
            "id": "input_release_time",
            "placeholder": "please input release_time！"
        }
    )
    submit = SubmitField(
        label="add",
        render_kw={
            "class": "btn btn-primary"
        }
    )
class PwdForm(FlaskForm):
    old_pwd=PasswordField(
        label="password",
        validators=[
            DataRequired("password empty")
        ],
        description="password",
        render_kw={
            "class": "form-control",
            "placeholder": "input old password",
            # "required": "required"
        }
    )
    new_pwd = PasswordField(
        label="password",
        validators=[
            DataRequired("password empty")
        ],
        description="password",
        render_kw={
            "class": "form-control",
            "placeholder": "input new password",
            # "required": "required"
        }
    )
    submit = SubmitField(
        label="edit",
        render_kw={
            "class": "btn btn-primary btn-block btn-flat"
        }
    )
    def validate_oldpwd(self,field):
        from flask import session
        pwd=field.data
        name=session["admin"]
        admin= Admin.query.filter_by(name=name).first()
        if not admin.check_pwd(pwd):
            print("pwd wrong",pwd)
            raise ValidationError("wrong password")

class AuthForm(FlaskForm):
    name = StringField(
        label="auth_name",
        validators=[
            DataRequired("auth name empty")
        ],
        description="auth name",
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "please input auth name！"
        }
    )
    url = StringField(
        label="url",
        validators=[
            DataRequired("url empty")
        ],
        description="url",
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "please input url！"
        }
    )
    submit = SubmitField(
        label="add",
        render_kw={
            "class": "btn btn-primary"
        }
    )
class RoleForm(FlaskForm):
    auth_list=Auth.query.all()
    name = StringField(
        label="role_name",
        validators=[
            DataRequired("role name empty")
        ],
        description="role name",
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "please input role name！"
        }
    )
    auths_list = SelectMultipleField(
        label="auths",
        validators=[
            DataRequired("auths empty")
        ],
        coerce=int,
        choices=[(v.id,v.name) for v in auth_list],
        description="auths list",
        render_kw={
            "class": "form-control"
        }
    )
    submit = SubmitField(
        label="add",
        render_kw={
            "class": "btn btn-primary"
        }
    )

class AdminForm(FlaskForm):
    role_list = Role.query.all()
    name = StringField(
        label="admin name",
        validators=[
            DataRequired("admin name empty")
        ],
        description="admin name",
        render_kw={
            "class": "form-control",
            "placeholder": "input admin name",
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
            DataRequired("password empty")
        ],
        description="password",
        render_kw={
            "class": "form-control",
            "placeholder": "input password",
            # "required": "required"
        }
    )
    role_id=SelectField(
        label="role",
        coerce=int,
        choices=[(v.id,v.name) for v in role_list],
        render_kw={
            "class": "form-control",
        }
    )
    submit = SubmitField(
        label="login",
        render_kw={
            "class": "btn btn-primary btn-block btn-flat"
        }
    )
