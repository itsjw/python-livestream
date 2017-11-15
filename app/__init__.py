#encoding:utf8

#encoding:utf8

from flask import Flask,render_template
import pymysql
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from app import config

app=Flask(__name__)
#app.config["SQLALCHEMY_DATABASE_URI"]="mysql+mysqldb://root:qaz123456@127.0.0.1:3306/movie"
app.config.from_object(config)
db=SQLAlchemy(app)

from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint,url_prefix="/admin")

@app.errorhandler(404)
def page_not_found(error):
    return  render_template("common/404.html"),404