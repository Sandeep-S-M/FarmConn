from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='farmer') # nursery, farmer
    
    # Common profile fields
    bio = db.Column(db.String(500))
    location = db.Column(db.String(128)) # Acts as Address
    
    # Nursery Specific Fields
    nursery_name = db.Column(db.String(128))
    owner_name = db.Column(db.String(128)) # New field
    contact_details = db.Column(db.String(256))
    payment_methods = db.Column(db.String(256))
    
    products = db.relationship('Product', backref='seller', lazy='dynamic')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.receiver_id',
                                        backref='recipient', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(128))
    breed = db.Column(db.String(128)) # New field
    description = db.Column(db.String(1000))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer, default=0) # New field
    image_url = db.Column(db.String(256))
    plant_age_days = db.Column(db.Integer) # New field
    available_days = db.Column(db.Integer) # New field
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(140))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<Post {self.title}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message {self.id}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    total_price = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending') # pending, accepted, rejected
    delivery_address = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    buyer = db.relationship('User', backref='orders_placed', foreign_keys=[buyer_id])
    product = db.relationship('Product', backref='orders')

    def __repr__(self):
        return f'<Order {self.id}>'
