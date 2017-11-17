#encoding:utf8

from datetime import datetime
from app import db

class User(db.Model):
    __tablename__="user"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100),unique=True)
    pwd=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(100),unique=True)
    phone=db.Column(db.String(11),unique=True)
    info=db.Column(db.Text)
    face=db.Column(db.String(255),unique=True)
    addtime=db.Column(db.DateTime,index=True,default=datetime.now)
    uuid=db.Column(db.String(255),unique=True)

    userlogs=db.relationship('UserLog',backref='user')
    comments=db.relationship('Comment',backref='user')
    moviecols = db.relationship('Moviecol', backref='user')
    # def __init__(self,id,name,pwd,email,phone,info,face,addtime,uid):
    #     self.id=id

    def __repr__(self):
        return '<User %r>'%self.name
    def check_pwd(self,pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd,pwd)

class UserLog(db.Model):
    __tablename__='userlog'
    id = db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    ip=db.Column(db.String(100))
    addtime=db.Column(db.DateTime,index=True,default=datetime.now)

    def __repr__(self):
        return '<Userlog %r>'%self.id

class Tag(db.Model):
    __tablename__='tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    movies=db.relationship("Movie",backref='tag')

    def __repr__(self):
        return '<Tag %r>'%self.name

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True)
    url = db.Column(db.String(255), unique=True)
    info = db.Column(db.Text)
    logo = db.Column(db.String(255), unique=True)
    star = db.Column(db.SmallInteger)
    playnum = db.Column(db.BigInteger)
    commentnum = db.Column(db.BigInteger)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    area = db.Column(db.String(255))
    releasetime = db.Column(db.Date)
    length=db.Column(db.String(100))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    comments = db.relationship('Comment', backref='movie')
    moviecols = db.relationship('Moviecol', backref='movie')
    def __repr__(self):
        return '<Movie %r>'%self.title

class Preview(db.Model):
    __tablename__='preview'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True)
    logo = db.Column(db.String(255), unique=True)
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<Preview %r>'%self.title

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text,nullable=False)
    movie_id= db.Column(db.Integer, db.ForeignKey('movie.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<Comment %r>'%self.title

class Moviecol(db.Model):
    __tablename__='moviecol'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<Moviecol %r>' % self.id

#authatation
class Auth(db.Model):
    __tablename__ = "auth"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    url = db.Column(db.String(100), unique=True)
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<Auth %r>'%self.name

class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    auths = db.Column(db.String(600), unique=True)
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    admins=db.relationship("Admin",backref="role")
    def __repr__(self):
        return '<role %r>'%self.name

#admin
class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    pwd = db.Column(db.String(100), nullable=False)
    is_super=db.Column(db.SmallInteger,nullable=False)  #super=1
    role_id=db.Column(db.Integer,db.ForeignKey('role.id'))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    adminlogs=db.relationship('AdminLog',backref='admin')
    oplogs = db.relationship('OpLog', backref='admin')

    def __repr__(self):
        return '<Admin %r>' % self.name
    def check_pwd(self,pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd,pwd)

class AdminLog(db.Model):
    __tablename__ = 'adminlog'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    ip = db.Column(db.String(100))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<Adminlog %r>' % self.id

class OpLog(db.Model):
    __tablename__ = 'oplog'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    ip = db.Column(db.String(100))
    reason=db.Column(db.String(600))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<Oplog %r>' % self.id

# if __name__=='__main__':
#     db.create_all()
    # role=Role(
    #     name='super admin',
    #     auths=''
    # )
    # db.session.add(role)
    # admin=Admin(
    #     name='imoocmovie1',
    #     pwd=generate_password_hash("imoocmovie1"),
    #     is_super=0,
    #     role_id=1
    # )
    # db.session.add(admin)
    # db.session.commit()