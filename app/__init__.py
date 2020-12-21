from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_dropzone import Dropzone
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__)
Bootstrap(app)
app.config.update(
DROPZONE_MAX_FILE_SIZE = 1024,
DROPZONE_TIMEOUT = 5*60*1000)


app.config['SECRET_KEY'] = 'hfja3435fjgklhj34643hksr4323sf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/noumy/OneDrive/Desktop/flaskFYP/project/site.db'
db = SQLAlchemy(app)
dropzone = Dropzone(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'



from app import routes
from app.models import User, Post, Package, Invoice
admin = Admin(app)
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Package, db.session))
admin.add_view(ModelView(Invoice, db.session))