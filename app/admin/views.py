#encoding:utf8
from . import admin
from flask import Flask,render_template,redirect,url_for,flash,session,request
from app.admin.forms import LoginForm,TagForm,MovieForm
from app.models import Admin,Tag,Movie,User
from functools import wraps
from app import db,app
from werkzeug.utils import secure_filename
import os,uuid,datetime

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

@admin.route('/tag/list/<int:page>/',methods=['GET','POST'])
@admin_login_req
def tag_list(page=None):
    if request.method == 'GET':
        if page is None:
            page=1
        page_data=Tag.query.order_by(Tag.addtime.desc()).paginate(page=page,per_page=10)
        return render_template("admin/tag_list.html",page_data=page_data)
    else:
        id=request.form.get("id")
        tag= Tag.query.filter_by(id=id).first_or_404()
        name = tag.name
        newname = request.form.get("name")
        if newname and name != newname:
            tag.name = newname
            db.session.add(tag)
            db.session.commit()
            flash("tag edit success", "ok")
        else:
            flash("tag edit fail", "error")
        return redirect(url_for("admin.tag_list", page=1))

@admin.route('/tag/delete/<int:id>/',methods=['GET','POST'])
@admin_login_req
def tag_delete(id=None):
    tag_del=Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag_del)
    db.session.commit()
    flash("tag delete","ok")
    return redirect(url_for("admin.tag_list",page=1))

# @admin.route('/tag/edit/<int:id>',methods=['POST','GET'])
# @admin_login_req
# def tag_edit():
#     form = TagForm()
#     if form.validate_on_submit():
#         data = form.data
#         tag = Tag.query.filter_by(id=id).first_or_404()
#         if tag and tag.name!=data["name"]:
#             db.session.add(tag)
#             db.session.commit()
#             flash("tag add success", "ok")
#         else:
#             flash("edit error, same name or wrong url","error")
#     return redirect(url_for("admin.tag_list",page=1))

def change_filename(filename):
    file_info=os.path.splitext(filename)
    filename=datetime.datetime.now().strftime("%Y%m%d%H%M%S")+str(uuid.uuid4().hex)+file_info[-1]
    return filename

@admin.route('/movie/add/',methods=['POST','GET'])
@admin_login_req
def movie_add():
    form =MovieForm()
    if form.validate_on_submit():
        data=form.data
        file_url=secure_filename(form.url.data.filename)
        file_logo=secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"],"rw")
        url=change_filename(file_url)
        logo=change_filename(file_logo)
        form.url.data.save(app.config["UP_DIR"]+url)
        form.logo.data.save(app.config["UP_DIR"]+logo)
        movie=Movie(
            title=data['title'],
            url=url,
            info=data['info'],
            logo=logo,
            star=int(data['star']),
            playnum=0,
            commentnum=0,
            tag_id=int(data['tag_id']),
            area=data['area'],
            releasetime=data["release_time"],
            length=data['length']
        )
        db.session.add(movie)
        db.session.commit()
        flash("movie add success","ok")
        return redirect(url_for('admin.movie_add'))
    return render_template("admin/movie_add.html",form=form)

@admin.route('/movie/list/<int:page>/')
@admin_login_req
def movie_list(page=None):
    if not page:
        page=1
    page_data = Movie.query.join(Tag).filter(Tag.id==Movie.tag_id).order_by(Movie.addtime.desc()).paginate(page=page, per_page=10)
    return render_template("admin/movie_list.html", page_data=page_data)

@admin.route('/movie/delete/<int:id>/')
@admin_login_req
def movie_delete(id=None):
    movie_del=Movie.query.filter_by(id=id).first_or_404()
    db.session.delete(movie_del)
    db.session.commit()

    flash("Movie delete","ok")
    return redirect(url_for("admin.movie_list",page=1))

@admin.route('/movie/edit/<int:id>/',methods=['POST','GET'])
@admin_login_req
def movie_edit(id):
    form =MovieForm()
    form.url.validators=[]
    form.logo.validators=[]
    movie=Movie.query.get_or_404(id)
    if request.method=="GET":
        form.info.data=movie.info
        form.tag_id.data=movie.tag_id
        form.star.data=movie.star
    #else
    if form.validate_on_submit():
        data=form.data
        title_count=Movie.query.filter_by(title=data['title']).count()
        if title_count==1 and movie.title!=data["title"]:
            flash("title exist", "error")
            return redirect(url_for('admin.movie_edit', id=movie.id))

        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], "rw")
        if form.url.data.filename!="":
            file_url = secure_filename(form.url.data.filename)
            movie.url = change_filename(file_url)
            form.url.data.save(app.config["UP_DIR"] + movie.url)

        if form.logo.data.filename != "":
            file_logo = secure_filename(form.logo.data.filename)
            movie.logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + movie.logo)

        movie.title=data["title"]
        movie.star = data["star"]
        movie.info = data["info"]
        movie.tag_id = data["tag_id"]
        movie.area = data["area"]
        movie.length = data["length"]
        movie.releasetime = data["release_time"]

        db.session.add(movie)
        db.session.commit()
        flash("movie add success","ok")
        return redirect(url_for('admin.movie_edit',id=movie.id))
    return render_template("admin/movie_edit.html",form=form,movie=movie)

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
def user_list(page=None):
    # if not page:
    #     page=1
    # page_data = User.query.order_by(User.addtime.desc()).paginate(page=page, per_page=10)
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