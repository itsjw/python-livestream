#encoding:utf8
from . import admin
from flask import Flask,render_template,redirect,url_for,flash,session,request
from app.admin.forms import LoginForm,TagForm
from app.models import Admin,Tag
from functools import wraps
from app import db

def admin_login_req(f):
    @wraps(f)
    def func(*args,**kwargs):
        if not session.get("admin"):
        # if "admin" not in session:
            return redirect(url_for("admin.login",next=request.url))
        return f(*args,**kwargs)
    return func


@admin.route('/')
@admin_login_req
def index():
    return render_template("admin/index.html")

@admin.route('/login/',methods=['POST','GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data=form.data
        admin=Admin.query.filter_by(name=data["account"]).first()
        if not admin.check_pwd(data['pwd']):
            flash("wrong password")
            return redirect(url_for('admin.login'))
        else:
            session["admin"]=data["account"]
            return redirect(request.args.get("next") or url_for("admin.index"))
    return render_template("admin/login.html",form=form)

@admin.route('/logout/')
@admin_login_req
def logout():
    session.pop("admin",None)
    return redirect(url_for("admin.login"))

@admin.route('/pwd/')
@admin_login_req
def pwd():
    return render_template("admin/pwd.html")

@admin.route('/tag/add/',methods=['POST','GET'])
@admin_login_req
def tag_add():
    form=TagForm()
    if form.validate_on_submit():
        data=form.data
        tag=Tag.query.filter_by(name=data["name"]).count()
        if tag ==1:
            flash("tag exit","error")
            return redirect(url_for("admin.tag_add"))
        else:
            tag=Tag(name=data["name"])
            db.session.add(tag)
            db.session.commit()
            flash("tag add success","ok")
            return redirect (url_for("admin.tag_add"))
    return render_template("admin/tag_add.html",form=form)

@admin.route('/tag/list/<int:page>/',methods=['GET'])
@admin_login_req
def tag_list(page=None):
    if page is None:
        page=1
    page_data=Tag.query.order_by(Tag.addtime.desc()).paginate(page=page,per_page=10)
    return render_template("admin/tag_list.html",page_data=page_data)

@admin.route('/tag/delete/<int:page>/',methods=['GET','POST'])
@admin_login_req
def tag_delete(page=None):
    if page is None:
        page=1
    page_data=Tag.query.order_by(Tag.addtime.desc()).paginate(page=page,per_page=10)
    return render_template("admin/tag_list.html",page_data=page_data)

@admin.route('/movie/add/')
@admin_login_req
def movie_add():
    return render_template("admin/movie_add.html")

@admin.route('/movie/list/')
@admin_login_req
def movie_list():
    return render_template("admin/movie_list.html")

@admin.route('/preview/add/')
@admin_login_req
def preview_add():
    return render_template("admin/preview_add.html")

@admin.route('/preview/list/')
@admin_login_req
def preview_list():
    return render_template("admin/preview_list.html")

@admin.route('/user/list/')
@admin_login_req
def user_list():
    return render_template("admin/user_list.html")

@admin.route('/user/view/')
@admin_login_req
def user_view():
    return render_template("admin/user_view.html")

@admin.route('/comment/list/')
@admin_login_req
def comment_list():
    return render_template("admin/comment_list.html")

@admin.route('/moviecol/list/')
@admin_login_req
def moviecol_list():
    return render_template("admin/moviecol_list.html")

@admin.route('/oplog/list/')
@admin_login_req
def oplog_list():
    return render_template("admin/oplog_list.html")

@admin.route('/adminloginlog/list/')
@admin_login_req
def adminloginlog_list():
    return render_template("admin/adminloginlog_list.html")

@admin.route('/userloginlog/list/')
@admin_login_req
def userloginlog_list():
    return render_template("admin/userloginlog_list.html")

@admin.route('/auth_add/list/')
@admin_login_req
def auth_add():
    return render_template("admin/auth_add.html")

@admin.route('/auth_list/list/')
@admin_login_req
def auth_list():
    return render_template("admin/auth_list.html")

@admin.route('/role_add/list/')
@admin_login_req
def role_add():
    return render_template("admin/role_add.html")

@admin.route('/role_list/list/')
@admin_login_req
def role_list():
    return render_template("admin/role_list.html")

@admin.route('/admin_add/list/')
@admin_login_req
def admin_add():
    return render_template("admin/admin_add.html")

@admin.route('/admin_list/list/')
@admin_login_req
def admin_list():
    return render_template("admin/admin_list.html")