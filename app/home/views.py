#encoding:utf8
from . import home
from flask import render_template,redirect,url_for,request,session,flash
from app.models import UserLog,db,User
from app.home.forms import *
from functools import wraps
from app import db,app
from werkzeug.security import generate_password_hash,check_password_hash
import uuid

def login_req(f):
    @wraps(f)
    def function(*args,**kwargs):
        if not session.get("id"):
            redirect(url_for("home.login"))
        return function
    return f


@home.route('/')
def index():
    return render_template("home/index.html")

@home.route('/animation/')
def animation():
    return render_template("home/animation.html")

@home.route('/login/',methods=["POST","GET"])
def login():
    if request.method=="GET":
        return render_template("home/login.html")
    else:
        name=request.form.get("name")
        pwd=request.form.get("pwd")
        user=User.query.filter(User.name==name).first()
        if not user:
            flash("user not exits","error")
            return redirect(url_for("home.login"))
        if not user.check_pwd(pwd):
            flash("wrong password","error")
            return redirect(url_for("home.login"))
        else:
            session["id"]=user.id
            session.permanent = True
            userlog = UserLog(
            user_id=session["id"],
            ip=request.remote_addr
            )
            db.session.add(userlog)
            db.session.commit()
            return redirect(url_for("home.index"))

@login_req
@home.route('/logout/')
def logout():
    session.pop("id",None)
    return redirect(url_for("home.login"))

@home.route('/regist/',methods=['POST','GET'])
def regist():
    form=UserForm()
    if form.validate_on_submit():
        data=form.data
        name=User.query.filter(User.name==data["name"]).first()
        email=User.query.filter(User.email==data["email"]).first()
        phone=User.query.filter(User.phone==data["phone"]).first()
        if name:
            flash("account name exist","error")
            return redirect(url_for('home.regist'))
        if email:
            flash("email exist","error")
            return redirect(url_for('home.regist'))
        if phone:
            flash("phone exist","error")
            return redirect(url_for('home.regist'))
        if data["pwd"]!=data["r_pwd"]:
            flash("password not same", "error")
            return redirect(url_for('home.regist'))
        user=User(
            name=data["name"],
            pwd=generate_password_hash(data["pwd"]),
            email=data["email"],
            phone=data["phone"],
            uuid=uuid.uuid4().hex
        )
        db.session.add(user)
        db.session.commit()
        flash("success","ok")
    return render_template("home/regist.html",form=form)

@login_req
@home.route('/user/')
def user():
    return render_template("home/user.html")

@login_req
@home.route('/pwd/')
def pwd():
    return render_template("home/pwd.html")


@home.route('/comments/')
def comments():
    return render_template("home/comments.html")

@login_req
@home.route('/loginlog/')
def loginlog():
    # page_data=UserLog.query.order_by(UserLog.addtime.desc()).paginate(page=page,per_page=10)
    return render_template("home/loginlog.html")

@login_req
@home.route('/moviecol/')
def moviecol():
    return render_template("home/moviecol.html")

@home.route('/search/')
def search():
    return render_template("home/search.html")

@home.route('/play/')
def play():
    return render_template("home/play.html")
