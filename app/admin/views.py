#encoding:utf8
from . import admin
from flask import render_template,redirect,url_for,flash,session,request,abort
from app.admin.forms import LoginForm,TagForm,MovieForm,PwdForm,AuthForm,RoleForm,AdminForm
from app.models import Admin,Tag,Movie,User,Comment,Moviecol,OpLog,AdminLog,UserLog,Auth,Role
from functools import wraps
from app import db,app
from werkzeug.utils import secure_filename
import os,uuid,datetime

@admin.context_processor
def tpl_extra():
    data=dict(
        online_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    return data

def admin_login_req(f):
    @wraps(f)
    def func(*args,**kwargs):
        if not session.get("admin"):
        # if "admin" not in session:
            return redirect(url_for("admin.login",next=request.url))
        return f(*args,**kwargs)
    return func


def admin_auth(f):
    @wraps(f)
    def func(*args,**kwargs):
        role=Role.query.join(Admin).filter(Admin.id==session['id'],Role.id==Admin.role_id).first()
        auth=list(map(lambda v:int(v),role.auths.split(' ')))
        auth_list=Auth.query.all()
        urls=[v.url for v in auth_list for val in auth if val==v.id]
        rule=request.url_rule
        print(urls,rule)
        if str(rule) not in urls:
            abort(404)
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
            flash("wrong password","error")
            return redirect(url_for('admin.login'))
        else:
            session["admin"]=data["account"]
            session["id"]=admin.id
            adminlog = AdminLog(
                admin_id=session["id"],
                ip=request.remote_addr
            )
            db.session.add(adminlog)
            db.session.commit()
            return redirect(request.args.get("next") or url_for("admin.index"))
    return render_template("admin/login.html",form=form)


@admin.route('/logout/')
@admin_login_req
def logout():
    session.pop("admin",None)
    session.pop("id",None)
    return redirect(url_for("admin.login"))

@admin.route('/pwd/',methods=["GET","POST"])
# @admin_login_req
def pwd():
    form=PwdForm()
    if form.validate_on_submit():
        data=form.data
        admin = Admin.query.filter_by(name=session["admin"]).first()
        if not admin.check_pwd(data['old_pwd']):
            flash("wrong password", "error")
            return redirect(url_for('admin.pwd'))

        else:
            from werkzeug.security import generate_password_hash
            admin.pwd=generate_password_hash(data["new_pwd"])

            db.session.add(admin)
            db.session.commit()
        flash("pwd change success", "ok")
        return redirect(url_for("admin.logout"))
    return render_template("admin/pwd.html",form=form)

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
            oplog=OpLog(
                admin_id=session["id"],
                ip=request.remote_addr,
                reason="add tag "+tag.name
            )
            db.session.add(oplog)
            db.session.commit()
            return redirect (url_for("admin.tag_add"))
    return render_template("admin/tag_add.html",form=form)

@admin.route('/tag/list/<int:page>/',methods=['GET','POST'])
@admin_login_req
def tag_list(page=1):
    if request.method == 'GET':
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
    oplog = OpLog(
        admin_id=session["id"],
        ip=request.remote_addr,
        reason="delete tag "+tag_del.name
    )
    db.session.add(oplog)
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
        oplog = OpLog(
            admin_id=session["id"],
            ip=request.remote_addr,
            reason="add movie "+movie.title
        )
        db.session.add(oplog)
        db.session.commit()
        flash("movie add success","ok")
        return redirect(url_for('admin.movie_add'))
    return render_template("admin/movie_add.html",form=form)

@admin.route('/movie/list/<int:page>/')
@admin_login_req
def movie_list(page=1):
    page_data = Movie.query.join(Tag).filter(Tag.id==Movie.tag_id).order_by(Movie.addtime.desc()).paginate(page=page, per_page=10)
    return render_template("admin/movie_list.html", page_data=page_data)

@admin.route('/movie/delete/<int:id>/')
@admin_login_req
def movie_delete(id=None):
    movie_del=Movie.query.filter_by(id=id).first_or_404()
    db.session.delete(movie_del)
    db.session.commit()
    oplog = OpLog(
        admin_id=session["id"],
        ip=request.remote_addr,
        reason="delete movie "+movie_del.title
    )
    db.session.add(oplog)
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
        oplog = OpLog(
            admin_id=session["id"],
            ip=request.remote_addr,
            reason="edit movie "+movie.title
        )
        db.session.add(oplog)
        db.session.commit()
        flash("movie add success","ok")
        return redirect(url_for('admin.movie_edit',id=movie.id))
    return render_template("admin/movie_edit.html",form=form,movie=movie)

@admin.route('/preview/add/')
@admin_auth
@admin_login_req
def preview_add():
    return render_template("admin/preview_add.html")

@admin.route('/preview/list/')
@admin_login_req
def preview_list():
    return render_template("admin/preview_list.html")

@admin.route('/user/list/<int:page>/')
@admin_login_req
def user_list(page=1):
    page_data = User.query.order_by(User.addtime.desc()).paginate(page=page, per_page=10)
    return render_template("admin/user_list.html",page_data=page_data)

@admin.route('/user/view/<int:id>/')
@admin_login_req
def user_view(id=None):
    user=User.query.get_or_404(id)
    return render_template("admin/user_view.html",user=user)

@admin.route('/user/delete/<int:id>/')
@admin_login_req
def user_delete(id=None):
    user=User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    oplog = OpLog(
        admin_id=session["id"],
        ip=request.remote_addr,
        reason="delete user "+user.name
    )
    db.session.add(oplog)
    db.session.commit()
    flash("delete success",'ok')
    return redirect(url_for("admin.user_list",page=1))

@admin.route('/comment/list/<int:page>/')
@admin_login_req
def comment_list(page=1):
    page_data = Comment.query.join(Movie).join(User).filter(Movie.id==Comment.movie_id,User.id==Comment.user_id).order_by(Comment.addtime.desc()).paginate(page=page, per_page=10)
    return render_template("admin/comment_list.html",page_data=page_data)

@admin.route('/comment/delete/<int:id>/')
@admin_login_req
def comment_delete(id=None):
    comment=Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    oplog = OpLog(
        admin_id=session["id"],
        ip=request.remote_addr,
        reason="delete comment "+comment.content
    )
    db.session.add(oplog)
    db.session.commit()
    flash("delete success",'ok')
    return redirect(url_for("admin.comment_list",page=1))

@admin.route('/moviecol/list/<int:page>/')
@admin_login_req
def moviecol_list(page=1):
    page_data = Moviecol.query.join(Movie).join(User).filter(Movie.id==Moviecol.movie_id,User.id==Moviecol.user_id).order_by(Moviecol.addtime.desc()).paginate(page=page, per_page=10)
    return render_template("admin/moviecol_list.html",page_data=page_data)

@admin.route('/moviecol/delete/<int:id>/')
@admin_login_req
def moviecol_delete(id=None):
    moviecol=Moviecol.query.get_or_404(id)
    db.session.delete(moviecol)
    db.session.commit()
    oplog = OpLog(
        admin_id=session["id"],
        ip=request.remote_addr,
        reason="delete moviecol "+moviecol.user_id+" "+moviecol.movie_id
    )
    db.session.add(oplog)
    db.session.commit()
    flash("delete success",'ok')
    return redirect(url_for("admin.moviecol_list",page=1))


@admin.route('/oplog/list/<int:page>/')
@admin_login_req
def oplog_list(page=1):
    page_data = OpLog.query.join(Admin).filter(Admin.id==OpLog.admin_id).order_by(OpLog.addtime.desc()).paginate(page=page, per_page=10)
    return render_template("admin/oplog_list.html",page_data=page_data)

@admin.route('/adminloginlog/list/<int:page>/')
@admin_login_req
def adminloginlog_list(page=1):
    page_data = AdminLog.query.join(Admin).filter(Admin.id==AdminLog.admin_id).order_by(AdminLog.addtime.desc()).paginate(page=page, per_page=10)
    return render_template("admin/adminloginlog_list.html",page_data=page_data)

@admin.route('/userloginlog/list/<int:page>/')
@admin_login_req
def userloginlog_list(page=1):
    page_data = UserLog.query.join(User).filter(User.id==UserLog.user_id).order_by(UserLog.addtime.desc()).paginate(page=page, per_page=10)
    return render_template("admin/userloginlog_list.html",page_data=page_data)

@admin.route('/auth_add/',methods=['POST','GET'])
@admin_login_req
def auth_add():
    form=AuthForm()
    if form.validate_on_submit():
        data=form.data
        auth = Auth.query.filter_by(name=data["name"]).count()
        if auth == 1:
            flash("auth name exit", "error")
            return redirect(url_for("admin.auth_add"))
        else:
            auth = Auth(name=data["name"],url=data["url"])
            db.session.add(auth)
            db.session.commit()
            flash("auth add success", "ok")
            oplog = OpLog(
                admin_id=session["id"],
                ip=request.remote_addr,
                reason="add auth " + auth.name
            )
            db.session.add(oplog)
            db.session.commit()
            return redirect(url_for("admin.auth_add"))
    return render_template("admin/auth_add.html",form=form)

@admin.route('/auth_list/list/<int:page>/')
@admin_login_req
def auth_list(page=1):
    page_data = Auth.query.order_by(Auth.addtime.desc()).paginate(page=page, per_page=10)
    return render_template("admin/auth_list.html",page_data=page_data)

@admin.route('/auth_list/delete/<int:id>/')
@admin_login_req
def auth_list_delete(id=None):
    auth_list=Auth.query.get_or_404(id)
    db.session.delete(auth_list)
    db.session.commit()
    oplog = OpLog(
        admin_id=session["id"],
        ip=request.remote_addr,
        reason="delete auth_list "+auth_list.name
    )
    db.session.add(oplog)
    db.session.commit()
    flash("delete success",'ok')
    return redirect(url_for("admin.auth_list",page=1))


@admin.route('/role_add/',methods=['POST','GET'])
@admin_login_req
def role_add():
    form = RoleForm()
    if form.validate_on_submit():
        data = form.data
        role = Role.query.filter_by(name=data["name"]).count()
        if role == 1:
            flash("role name exit", "error")
            return redirect(url_for("admin.role_add"))
        else:
            role = Role(name=data["name"],auths=" ".join(map(lambda v:str(v),data["auths_list"])))
            db.session.add(role)
            db.session.commit()
            flash("role add success", "ok")
            oplog = OpLog(
                admin_id=session["id"],
                ip=request.remote_addr,
                reason="add role " + role.name
            )
            db.session.add(oplog)
            db.session.commit()
            return redirect(url_for("admin.role_add"))
    return render_template("admin/role_add.html",form=form)

@admin.route('/role_list/list/<int:page>/')
@admin_login_req
def role_list(page=1):
    page_data = Role.query.order_by(Role.addtime.desc()).paginate(page=page, per_page=10)
    return render_template("admin/role_list.html",page_data=page_data)


@admin.route('/role_list/delete/<int:id>/')
@admin_login_req
def role_list_delete(id=None):
    role_list=Role.query.get_or_404(id)
    db.session.delete(role_list)
    db.session.commit()
    oplog = OpLog(
        admin_id=session["id"],
        ip=request.remote_addr,
        reason="delete role_list "+role_list.name
    )
    db.session.add(oplog)
    db.session.commit()
    flash("delete success",'ok')
    return redirect(url_for("admin.role_list",page=1))
# list(map(lambda v:int(v),auths.split(" ")))

@admin.route('/admin_add/',methods=['POST','GET'])
@admin_login_req
def admin_add():
    form=AdminForm()
    if form.validate_on_submit():
        data=form.data
        NewAdmin = Admin.query.filter_by(name=data["name"]).count()
        if NewAdmin == 1:
            flash("Admin name exit", "error")
            return redirect(url_for("admin.admin_add"))
        if data["pwd"]!=data["r_pwd"]:
            flash("pass word not same", "error")
            return redirect(url_for("admin.admin_add"))
        else:
            from werkzeug.security import generate_password_hash
            NewAdmin = Admin(name=data["name"], pwd=generate_password_hash(data["pwd"]), role_id=data["role_id"],is_super=0)
            db.session.add(NewAdmin)
            db.session.commit()
            flash("admin add success", "ok")
            oplog = OpLog(
                admin_id=session["id"],
                ip=request.remote_addr,
                reason="add role " + NewAdmin.name
            )
            db.session.add(oplog)
            db.session.commit()
            return redirect(url_for("admin.admin_add"))

    return render_template("admin/admin_add.html",form=form)

@admin.route('/admin_list/list/<int:page>/')
@admin_login_req
def admin_list(page=1):
    page_data = Admin.query.order_by(Admin.addtime.desc()).paginate(page=page, per_page=10)
    return render_template("admin/admin_list.html",page_data=page_data)

@admin.route('/admin_list/delete/<int:id>/')
@admin_login_req
def admin_list_delete(id=None):
    admin_list=Admin.query.get_or_404(id)
    db.session.delete(admin_list)
    db.session.commit()
    oplog = OpLog(
        admin_id=session["id"],
        ip=request.remote_addr,
        reason="delete admin_list "+admin_list.name
    )
    db.session.add(oplog)
    db.session.commit()
    flash("delete success",'ok')
    return redirect(url_for("admin.admin_list",page=1))