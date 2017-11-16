#coding:utf8
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,FileField,TextAreaField,SelectField
from wtforms.validators import DataRequired,ValidationError
from app.models import Admin,Tag

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