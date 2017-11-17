
import datetime,os
DEBUG=False
SECRET_KEY="ee511"
PERMANENT_SESSION_LIFETIME=datetime.timedelta(days=7)

username='root'
password='qaz123456'
host='127.0.0.1'
port='3306'
database='movie'
SQLALCHEMY_DATABASE_URI="mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8".format(username,password,host,port,database)
SQLALCHEMY_TRACK_MODIFICATIONS = True
UP_DIR=os.path.join(os.path.abspath(os.path.dirname(__file__)),"static/uploads/")
