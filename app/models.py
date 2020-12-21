from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(125), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(600), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    package = db.Column(db.String(30))
    country = db.Column(db.String(30))
    address = db.Column(db.Text)
    bucket_name = db.Column(db.String(300))
    region = db.Column((db.String(50)))
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"User('{self.title}', '{self.date_posted}')"


class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    package_name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.String(10))
    duration = db.Column(db.String(10))
    storage_capacity=db.Column(db.String(10))

    def __repr__(self):
        return f"User('{self.title}', '{self.price}', '{self.user_id.name}')"

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"User('{self.title}', '{self.price}', '{self.user_id.name}')"