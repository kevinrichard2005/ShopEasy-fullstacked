import os
import sys

# More aggressive path injection for Render/Production
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


from flask import Flask, send_from_directory
from flask_login import LoginManager
from config import Config
try:
    from models import db, User, Product
except ImportError as e:
    print(f"SHOEASY_ERROR: Failed to import models: {e}")
    # Fallback or re-raise with more info
    raise

def create_app():
    """Application factory."""
    app = Flask(
        __name__,
        template_folder='.',       # HTML templates served from ROOT folder
        static_folder='static',    # Static files from static/
        static_url_path='/static'
    )
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprint
    from routes import main
    app.register_blueprint(main)
    
    # Serve root style.css
    @app.route('/style.css')
    def root_style():
        return send_from_directory('.', 'style.css', mimetype='text/css')
    
    # Serve product images from root (for existing images like shirt1.jpg, etc.)
    @app.route('/images/<path:filename>')
    def root_images(filename):
        return send_from_directory('.', filename)
    
    # Serve static images
    @app.route('/static/images/<path:filename>')
    def static_images(filename):
        return send_from_directory(os.path.join('static', 'images'), filename)
    
    # Create database tables and seed data
    with app.app_context():
        # Ensure instance folder exists for SQLite
        os.makedirs(app.instance_path, exist_ok=True)
        db.create_all()
        seed_data()
    
    return app


def seed_data():
    """Seed database with initial data."""
    # Create admin user if not exists
    if not User.query.filter_by(email='admin@shopeasy.com').first():
        admin = User(username='admin', email='admin@shopeasy.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
    
    # Seed products
    if Product.query.count() == 0:
        products = [
            Product(
                name='Casual Brown Shirt',
                description='Comfortable brown long-sleeve shirt. Great for daily wear.',
                price=349.00,
                original_price=699.00,
                image='shirt1.jpg',
                category='Shirts',
                stock=100,
                featured=True
            ),
            Product(
                name='Classic Checked Shirt',
                description='Blue and white checked shirt in soft cotton. Standard fit.',
                price=399.00,
                original_price=799.00,
                image='shirt2.jpg',
                category='Shirts',
                stock=80,
                featured=True
            ),
            Product(
                name='Daily Walk Sneakers',
                description='Lightweight blue and white sneakers for daily use. Breathable.',
                price=599.00,
                original_price=1299.00,
                image='sneaker.jpg',
                category='Footwear',
                stock=75,
                featured=True
            ),
            Product(
                name='Comfort Grip Trainers',
                description='Beige and green trainers with a thick sole for comfort.',
                price=649.00,
                original_price=1499.00,
                image='sneaker1.jpg',
                category='Footwear',
                stock=60,
                featured=True
            ),
            Product(
                name='Colorful Casual Shoes',
                description='Bright multi-color shoes for a fun, everyday look.',
                price=499.00,
                original_price=999.00,
                image='shoe.jpg',
                category='Footwear',
                stock=55,
                featured=False
            ),
            Product(
                name='City Style Sneakers',
                description='Simple multi-color sneakers for city walks.',
                price=549.00,
                original_price=1199.00,
                image='shoe1.jpg',
                category='Footwear',
                stock=45,
                featured=False
            ),
            Product(
                name='Striped Polo T-Shirt',
                description='Navy and grey striped polo shirt. Smart-casual look.',
                highlights='Comfortable Fit|Easy Wash|Standard Style|Multiple Sizes',
                price=249.00,
                original_price=499.00,
                image='tshirt1.jpg',
                category='T-Shirts',
                stock=120,
                sizes='S,M,L,XL,XXL',
                featured=True
            ),
            Product(
                name='Plain White Tee',
                description='Basic white t-shirt. 100% cotton, soft and durable.',
                highlights='Pure Cotton|Regular Fit|White Color|Daily Essential',
                price=199.00,
                original_price=399.00,
                image='tshirt2.jpg',
                category='T-Shirts',
                stock=150,
                sizes='S,M,L,XL',
                featured=False
            ),
            Product(
                name='Purple Graphic Tee',
                description='Ladies light purple t-shirt with a simple dandelion print.',
                highlights='Soft Fabric|Flower Print|Purple Color|Ladies Fit',
                price=249.00,
                original_price=549.00,
                image='tshirtw1.jpg',
                category='T-Shirts',
                stock=90,
                sizes='XS,S,M,L,XL',
                featured=True
            ),
            Product(
                name='Smart Health Watch',
                description='Smartwatch with health tracking features and long battery.',
                highlights='Step Counter|Heart Monitor|Calls Sync|Long Battery',
                price=799.00,
                original_price=1599.00,
                image='watch.jpg',
                category='Watches',
                stock=40,
                featured=True
            ),
            Product(
                name='Waterproof Sport Watch',
                description='Rugged digital watch that is water resistant up to 50m.',
                highlights='Water Resistant|Sport Design|Timer/Alarm|Comfortable Strap',
                price=849.00,
                original_price=1799.00,
                image='watch1.jpg',
                category='Watches',
                stock=30,
                featured=True
            ),
            Product(
                name='Square Digital Watch',
                description='Sleek square-shaped digital watch with health monitoring.',
                price=699.00,
                original_price=1399.00,
                image='watch2.jpg',
                category='Watches',
                stock=50,
                featured=False
            ),
            Product(
                name='Wired Music Headphones',
                description='Over-ear wired headphones with clear audio performance.',
                price=349.00,
                original_price=799.00,
                image='wiredheadphone1.jpg',
                category='Electronics',
                stock=60,
                featured=False
            ),
            Product(
                name='Simple Wired Earphones',
                description='Compact in-ear wired earphones with inline microphone.',
                price=149.00,
                original_price=299.00,
                image='wiredheadphone2.jpg',
                category='Electronics',
                stock=100,
                featured=False
            ),
            Product(
                name='Portable Mini Speaker',
                description='Small Bluetooth speaker with big sound for travel.',
                price=449.00,
                original_price=949.00,
                image='speaker1.jpg',
                category='Electronics',
                stock=85,
                featured=True
            ),
            Product(
                name='Classic Bluetooth Speaker',
                description='Bluetooth speaker with retro design and clear audio.',
                price=899.00,
                original_price=1999.00,
                image='speaker2.jpg',
                category='Electronics',
                stock=25,
                featured=False
            ),
        ]
        db.session.add_all(products)
    
    db.session.commit()


# Create and run the app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, use_debugger=False, host='0.0.0.0', port=5000)
