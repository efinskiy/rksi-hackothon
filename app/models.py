from . import db
from flask_login import UserMixin

class Settings(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String)
    value = db.Column(db.String)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    is_kitchen = db.Column(db.Boolean)
    is_admin = db.Column(db.Boolean)


class Menu(db.Model):
    __tablename__ = 'menu'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    weight = db.Column(db.Integer)
    img = db.Column(db.String)
    price = db.Column(db.Float, nullable = False)
    balance = db.Column(db.Integer)
    basket = db.relationship('Basket', backref = 'menu')

class Coupon(db.Model):
    __tablename__ = 'coupons'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String)
    discount = db.Column(db.Integer)
    count = db.Column(db.Integer)

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    
    order = db.relationship('Order', backref='customer')
    basket = db.relationship('Basket', backref = 'customer')
    

class Basket(db.Model):
    __tablename__ = 'basket'

    id = db.Column(db.Integer, primary_key = True)
    amount = db.Column(db.Integer)
    
    cust_id = db.Column(db.Integer, db.ForeignKey(Customer.id))
    item = db.Column(db.Integer, db.ForeignKey(Menu.id))

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey(Customer.id))
    confirmation_code = db.Column(db.Integer, nullable=False)
    items = db.Column(db.String)
    ord_price = db.Column(db.Float, nullable = False)
    date = db.Column(db.DateTime)
    status = db.Column(db.Integer)