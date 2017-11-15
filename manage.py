#encoding:utf8
from app import app

if __name__=="__main__":
    app.run(debug=True)

# from flask_script import Manager
# from flask_migrate import Migrate,MigrateCommand
# from root import app
# from exts import db
#
# manager=Manager(app)
#
# #use migrate to connect app and db
# migrate=Migrate(app,db)
#
# #add migratecommand to db
# manager.add_command('db',MigrateCommand)
#
# if __name__=="__main__":
#     manager.run()