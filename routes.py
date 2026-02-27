from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Product, CartItem, Order, OrderItem
from werkzeug.utils import secure_filename
import os
import json

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ──────────────── PAGE ROUTES ────────────────

@main.route('/')
def index():
    featured_products = Product.query.filter_by(featured=True).limit(8).all()
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories]
    all_products = Product.query.order_by(Product.created_at.desc()).limit(12).all()
    return render_template('index.html', 
                         featured_products=featured_products, 
                         all_products=all_products,
                         categories=categories)


@main.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    related = Product.query.filter(
        Product.category == product.category, 
        Product.id != product.id
    ).limit(4).all()
    return render_template('product.html', product=product, related_products=related)


@main.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=bool(remember))
            flash('Welcome back!', 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
        
        flash('Invalid email or password.', 'error')
    
    return render_template('login.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or not email or not password:
            flash('All fields are required.', 'error')
        elif password != confirm_password:
            flash('Passwords do not match.', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
        elif User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Registration successful!', 'success')
            return redirect(url_for('main.index'))
            
    return render_template('register.html')


@main.route('/forgot-password')
def forgot_password():
    flash('Password reset functionality is coming soon. Please contact support.', 'info')
    return redirect(url_for('main.login'))


@main.route('/checkout')
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('main.cart'))
    total = sum(item.product.price * item.quantity for item in cart_items)
    razorpay_key = current_app.config.get('RAZORPAY_KEY_ID', '')
    return render_template('checkout.html', cart_items=cart_items, total=total, razorpay_key=razorpay_key)


@main.route('/success')
@login_required
def success():
    order_id = request.args.get('order_id')
    order = None
    if order_id:
        order = Order.query.get(order_id)
    return render_template('success.html', order=order)


@main.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        products = Product.query.filter(
            db.or_(
                Product.name.ilike(f'%{query}%'),
                Product.description.ilike(f'%{query}%'),
                Product.category.ilike(f'%{query}%')
            )
        ).all()
    else:
        products = []
    return render_template('index.html', 
                         featured_products=products, 
                         all_products=products,
                         categories=[],
                         search_query=query)


@main.route('/category/<category_name>')
def category(category_name):
    products = Product.query.filter_by(category=category_name).all()
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories]
    return render_template('index.html',
                         featured_products=[],
                         all_products=products,
                         categories=categories,
                         search_query=category_name)


# ──────────────── AUTH ROUTES ────────────────



@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


# ──────────────── CART API ROUTES ────────────────

@main.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Please login to add items to cart'}), 401
    data = request.get_json() or request.form
    product_id_raw = data.get('product_id')
    if not product_id_raw:
        return jsonify({'success': False, 'message': 'Product ID is required'}), 400
        
    try:
        product_id = int(product_id_raw)
        quantity = int(data.get('quantity', 1))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid product ID or quantity'}), 400
        
    size = data.get('size')
    if size == "": # Treat empty string as None
        size = None
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    
    if product.stock < quantity:
        return jsonify({'success': False, 'message': 'Not enough stock'}), 400
    
    # Check if this precise item (product + size) already in cart
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id, size=size).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity, size=size)
        db.session.add(cart_item)
    
    db.session.commit()
    
    # Calculate total quantity for the badge
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    cart_count = sum(item.quantity for item in cart_items)
    return jsonify({'success': True, 'message': 'Added to cart!', 'cart_count': cart_count})


@main.route('/api/cart/update', methods=['POST'])
def update_cart():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data = request.get_json() or request.form
    item_id = data.get('item_id')
    quantity = int(data.get('quantity', 1))
    
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not cart_item:
        return jsonify({'success': False, 'message': 'Cart item not found'}), 404
    
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity
    
    db.session.commit()
    
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    cart_count = sum(item.quantity for item in cart_items)
    
    return jsonify({'success': True, 'total': total, 'cart_count': cart_count})


@main.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data = request.get_json() or request.form
    item_id = data.get('item_id')
    
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not cart_item:
        return jsonify({'success': False, 'message': 'Cart item not found'}), 404
    
    db.session.delete(cart_item)
    db.session.commit()
    
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    cart_count = sum(item.quantity for item in cart_items)
    
    return jsonify({'success': True, 'total': total, 'cart_count': cart_count})


@main.route('/api/cart/count')
def cart_count():
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        count = sum(item.quantity for item in cart_items)
    else:
        count = 0
    return jsonify({'count': count})


# ──────────────── ORDER / CHECKOUT ROUTES ────────────────

@main.route('/api/checkout', methods=['POST'])
@login_required
def process_checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        return jsonify({'success': False, 'message': 'Cart is empty'}), 400
    
    data = request.get_json() or request.form
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    order = Order(
        user_id=current_user.id,
        total_amount=total,
        status='Pending',
        full_name=data.get('full_name', ''),
        address=data.get('address', ''),
        city=data.get('city', ''),
        state=data.get('state', ''),
        zipcode=data.get('zipcode', ''),
        phone=data.get('phone', ''),
        payment_id=data.get('payment_id', ''),
        razorpay_order_id=data.get('razorpay_order_id', '')
    )
    db.session.add(order)
    db.session.flush()
    
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.price,
            size=cart_item.size
        )
        db.session.add(order_item)
        
        # Update stock
        cart_item.product.stock -= cart_item.quantity
        
        # Remove from cart
        db.session.delete(cart_item)
    
    order.status = 'Paid' if (data.get('payment_id') or data.get('payment_method') == 'free') else 'Pending'
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Order placed successfully!',
        'order_id': order.id
    })


# ──────────────── ADMIN ROUTES ────────────────

@main.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin only.', 'error')
        return redirect(url_for('main.index'))
    
    products = Product.query.order_by(Product.created_at.desc()).all()
    orders = Order.query.order_by(Order.created_at.desc()).limit(20).all()
    users = User.query.all()
    
    stats = {
        'total_products': Product.query.count(),
        'total_orders': Order.query.count(),
        'total_users': User.query.count(),
        'total_revenue': db.session.query(db.func.sum(Order.total_amount)).filter_by(status='Paid').scalar() or 0
    }
    
    return render_template('admin.html', products=products, orders=orders, users=users, stats=stats)


@main.route('/admin/product/add', methods=['POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    price = float(request.form.get('price', 0))
    original_price = request.form.get('original_price')
    original_price = float(original_price) if original_price else None
    category = request.form.get('category', 'General').strip()
    stock = int(request.form.get('stock', 0))
    featured = request.form.get('featured') == 'on'
    highlights = request.form.get('highlights', '').strip()
    sizes = request.form.get('sizes', '').strip()
    
    image_filename = 'default.jpg'
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            image_filename = secure_filename(file.filename)
            upload_path = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_path, exist_ok=True)
            file.save(os.path.join(upload_path, image_filename))
    
    product = Product(
        name=name,
        description=description,
        price=price,
        original_price=original_price,
        image=image_filename,
        category=category,
        stock=stock,
        featured=featured,
        highlights=highlights,
        sizes=sizes
    )
    db.session.add(product)
    db.session.commit()
    
    flash('Product added successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))


@main.route('/admin/product/edit/<int:product_id>', methods=['POST'])
@login_required
def edit_product(product_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    product = Product.query.get_or_404(product_id)
    
    product.name = request.form.get('name', product.name).strip()
    product.description = request.form.get('description', product.description).strip()
    product.price = float(request.form.get('price', product.price))
    original_price = request.form.get('original_price')
    product.original_price = float(original_price) if original_price else None
    product.category = request.form.get('category', product.category).strip()
    product.stock = int(request.form.get('stock', product.stock))
    product.featured = request.form.get('featured') == 'on'
    product.highlights = request.form.get('highlights', product.highlights)
    product.sizes = request.form.get('sizes', product.sizes)
    
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            image_filename = secure_filename(file.filename)
            upload_path = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_path, exist_ok=True)
            file.save(os.path.join(upload_path, image_filename))
            product.image = image_filename
    
    db.session.commit()
    flash('Product updated successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))


@main.route('/admin/product/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))


# ──────────────── API ROUTES ────────────────

@main.route('/api/products')
def api_products():
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = Product.query
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%')
            )
        )
    
    products = query.order_by(Product.created_at.desc()).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': p.price,
        'original_price': p.original_price,
        'image': p.image,
        'category': p.category,
        'stock': p.stock,
        'featured': p.featured,
        'discount_percent': p.discount_percent,
        'highlights': p.highlights,
        'sizes': p.sizes
    } for p in products])


@main.route('/api/product/<int:product_id>')
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'original_price': product.original_price,
        'category': product.category,
        'stock': product.stock,
        'featured': product.featured,
        'image': product.image,
        'highlights': product.highlights,
        'sizes': product.sizes
    })
