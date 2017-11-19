#encoding:utf8
from . import home
from flask import render_template,redirect,url_for,request,session,flash,Response
from app.models import UserLog,User,Tag,Movie,Comment,Moviecol
from app.home.forms import *
from functools import wraps
from app import db,app,rd
from werkzeug.security import generate_password_hash,check_password_hash
import uuid,os,datetime


def login_req(f):
    @wraps(f)
    def func(*args,**kwargs):
        if not session.get("id"):
            redirect(url_for("home.login"))
        return f(*args,**kwargs)
    return func

def change_filename(filename):
    file_info=os.path.splitext(filename)
    filename=datetime.datetime.now().strftime("%Y%m%d%H%M%S")+str(uuid.uuid4().hex)+file_info[-1]
    return filename

@home.route('/<int:page>/')
def index(page=1):
    tags=Tag.query.all()

    tid=request.args.get("tid",0)
    page_data=Movie.query
    if int(tid)!=0:
        page_data=page_data.filter_by(tag_id=tid)

    star=int(request.args.get("star",0))
    if star!=0:
        page_data=page_data.filter_by(star=star)


    time= int(request.args.get("time",0))
    if time!=0:
        if time==1:
            page_data=page_data.order_by(Movie.addtime.desc())
        else:
            page_data=page_data.order_by(Movie.addtime.asc())

    pn=int(request.args.get("pn",0))
    if pn!=0:
        if pn==1:
            page_data=page_data.order_by(Movie.playnum.desc())
        else:
            page_data=page_data.order_by(Movie.playnum.asc())

    cn=int(request.args.get("cn",0))
    if cn!=0:
        if cn==1:
            page_data=page_data.order_by(Movie.commentnum.desc())
        else:
            page_data=page_data.order_by(Movie.commentnum.asc())

    page_data=page_data.paginate(page=page,per_page=10)
    p=dict(
        tid=tid,
        star=star,
        time=time,
        pn=pn,
        cn=cn
    )
    return render_template("home/index.html",tags=tags,p=p,page_data=page_data)

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
            return redirect(url_for("home.index",page=1))

@home.route('/logout/')
@login_req
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


@home.route('/user/',methods=['POST','GET'])
@login_req
def user():
    form=UserInfo()
    if request.method == "GET":
        if session.get('id'):
            user = User.query.get(int(session["id"]))
            form.email.data = user.email
            form.phone.data = user.phone
            form.info.data = user.info
            return render_template("home/user.html", form=form,user=user)
        else:
            return redirect(url_for("home.login"))

    user = User.query.get(int(session["id"]))
    if form.validate_on_submit():
        data=form.data
        if not os.path.exists(app.config["FC_DIR"]):
            os.makedirs(app.config["FC_DIR"])
            os.chmod(app.config["FC_DIR"],"rw")
        if data["face"]:
            form.face.data.save(app.config["FC_DIR"]+user.name)


        if User.query.filter_by(email=data["email"]).count()==0:
            user.email = data["email"]
        else:
            flash("email exist", "error")

        if User.query.filter_by(phone=data["phone"]).count()==0:
            user.phone = data["phone"]
        else:
            flash("phone exist", "error")

        user.info = data["info"]
        db.session.add(user)
        db.session.commit()
        flash("edit success", "ok")
        return redirect(url_for('home.user'))
    return render_template("home/user.html",form=form,user=user)

@home.route('/pwd/',methods=["POST","GET"])
@login_req
def pwd():
    form=PwdForm()
    if form.validate_on_submit():
        data=form.data
        user=User.query.filter(User.id==session["id"]).first()
        if check_password_hash(user.pwd,data["old_pwd"]):
            user.pwd=generate_password_hash(data["new_pwd"])
            db.session.add(user)
            db.session.commit()
            flash("change password success", "ok")
        else:
            flash("old password wrong","error")
    return render_template("home/pwd.html",form=form)


@home.route('/animation/')
def animation():
    return render_template("home/animation.html")


@home.route('/comments/<int:page>/')
def comments(page=1):
    page_data=Comment.query.join(User).filter(Comment.user_id==session["id"]).order_by(Comment.addtime.desc()).paginate(page=page,per_page=10)
    return render_template("home/comments.html",page_data=page_data)


@home.route('/loginlog/')
@login_req
def loginlog():
    # page_data=UserLog.query.order_by(UserLog.addtime.desc()).paginate(page=page,per_page=10)
    return render_template("home/loginlog.html")


@home.route('/addCol/')
@login_req
def addCol():
    import json
    m_id=request.args.get("m_id","")
    moviecol=Moviecol.query.filter_by(user_id=session['id'],movie_id=int(m_id)).first()
    print(session["id"], " ", m_id)
    if m_id and not moviecol:
        data=dict(ok=1)
        moviecol=Moviecol(movie_id=m_id,
        user_id=session["id"])
        db.session.add(moviecol)
        db.session.commit()
    else:
        data=dict(ok=0)

    # page_data=UserLog.query.order_by(UserLog.addtime.desc()).paginate(page=page,per_page=10)
    return json.dumps(data)

@home.route('/moviecol/<int:page>/')
@login_req
def moviecol(page=1):
    page_data=Moviecol.query.join(Movie).join(User).filter(Moviecol.movie_id==Movie.id,Moviecol.user_id==session["id"]).order_by(Moviecol.addtime.desc()).paginate(page=page,per_page=10)
    return render_template("home/moviecol.html",page_data=page_data)

@home.route('/search/<int:page>/')
def search(page=1):
    if page==0:
        page=1
    key=request.args.get("key","")
    page_data = Movie.query.filter(Movie.title.ilike('%'+key+'%')).order_by(Movie.addtime.desc()).paginate(page=page,per_page=10)
    page_data.key=key
    return render_template("home/search.html",key=key,page_data=page_data)

@home.route('/play/<int:id>/<int:page>/', methods=["POST","GET"])
def play(id=None,page=1):
    movie=Movie.query.get_or_404(id)
    comment=Comment.query.join(Movie).join(User).filter(Movie.id==movie.id,Comment.user_id==User.id).order_by(Comment.addtime.desc()).paginate(page=page,per_page=10)
    form = CommentForm()
    movie.playnum = movie.playnum + 1
    if session.get("id") and form.validate_on_submit():
        data=form.data
        add_c=Comment(
            content=data["info"],
            movie_id=movie.id,
            user_id=session["id"]
        )
        db.session.add(add_c)
        db.session.commit()
        movie.commentnum=movie.commentnum+1
        flash("comment add!","ok")
        db.session.add(movie)
        db.session.commit()
        return redirect(url_for('home.play',id=movie.id,page=1))
    else:
        db.session.add(movie)
        db.session.commit()
    return render_template("home/play.html",movie=movie,comment=comment,form=form)

@home.route('/tm/',methods=['GET','POST'])
def tm():
    import json
    # send danmaku
    if request.method=="GET":
        id=request.args.get("id")
        key="movie"+str(id)
        if rd.llen(key):
            msgs=rd.lrange(key,0,2999)
            res={
                "code":1,
                "danmaku":[json.loads(v.decode('utf-8')) for v in msgs]
            }
        else:
            res={
                "code":1,
                "danmaku":[]
            }
        resp=json.dumps(res)
    else:
        #add danmaku
        data=json.loads(request.get_data().decode('utf-8'))
        msg={
            "__v":0,
            "autho":data["author"],
            "time":data["time"],
            "text":data["text"],
            "color":data["color"],
            "type":data["type"],
            "ip":request.remote_addr,
            "_id":datetime.datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex,
            "player":[data["player"]]
        }
        res={
            "code":1,
            "data":msg
        }
        resp=json.dumps(res)
        rd.lpush("movie"+str(data["player"]),json.dumps(msg))
    return Response(resp,mimetype="application/json")