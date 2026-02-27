from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Product(db.Model):
    """Product model."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    highlights = db.Column(db.Text, nullable=True) # "About this item" bullet points
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float, nullable=True)
    image = db.Column(db.String(300), nullable=False, default='default.jpg')
    category = db.Column(db.String(100), nullable=False, default='General')
    stock = db.Column(db.Integer, nullable=False, default=0)
    featured = db.Column(db.Boolean, default=False)
    sizes = db.Column(db.String(200), nullable=True) # Comma-separated sizes like "S,M,L,XL"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cart_items = db.relationship('CartItem', backref='product', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0
    
    @property
    def highlights_list(self):
        if self.highlights:
            return [h.strip() for h in self.highlights.split('|') if h.strip()]
        return []

    @property
    def sizes_list(self):
        if self.sizes:
            return [s.strip() for s in self.sizes.split(',') if s.strip()]
        return []
    
    def __repr__(self):
        return f'<Product {self.name}>'


class CartItem(db.Model):
    """Shopping cart item model."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    size = db.Column(db.String(20), nullable=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CartItem user={self.user_id} product={self.product_id}>'


class Order(db.Model):
    """Order model."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    payment_id = db.Column(db.String(200), nullable=True)
    razorpay_order_id = db.Column(db.String(200), nullable=True)
    
    # Shipping details
    full_name = db.Column(db.String(200), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    zipcode = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.id}>'


class OrderItem(db.Model):
    """Order item model."""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    size = db.Column(db.String(20), nullable=True)
    
    def __repr__(self):
        return f'<OrderItem order={self.order_id} product={self.product_id}>'
