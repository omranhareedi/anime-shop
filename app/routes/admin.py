import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, current_app
from app import db
from app.models import Product, Order, OrderItem, Category, Vendor, login_required
from app.security import make_token, sanitize_form_data
from sqlalchemy import func


def save_upload(file):
    if file and file.filename:
        filename = secure_filename(file.filename)
        folder = os.path.join(current_app.static_folder, 'images', 'products')
        os.makedirs(folder, exist_ok=True)
        file.save(os.path.join(folder, filename))
        return filename
    return None

admin_bp = Blueprint('admin', __name__)


def row_to_dict(row):
    return {key: getattr(row, key) for key in row._fields}


def slugify(text):
    import re
    text = text.strip().lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


@admin_bp.route('/products')
@login_required
def product_list():
    products = Product.query.order_by(Product.id).all()
    return render_template('admin/products.html', products=products)


@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.order_by(Category.name).all()
    vendors = Vendor.query.order_by(Vendor.name).all()

    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token', '')
        if not csrf_token or csrf_token != request.cookies.get('csrf_token'):
            flash('Security token invalid.', 'danger')
            return redirect(url_for('admin.product_edit', product_id=product.id))

        sanitized = sanitize_form_data(request.form, {
            'name': {'max_length': 200},
            'slug': {'max_length': 200},
            'description': {'max_length': 5000},
            'genre': {'max_length': 100},
        })

        slug = sanitized['slug'] or slugify(sanitized['name'])
        existing = Product.query.filter(Product.slug == slug, Product.id != product.id).first()
        if existing:
            flash('A product with that slug already exists.', 'danger')
            return redirect(url_for('admin.product_edit', product_id=product.id))

        product.name = sanitized['name']
        product.slug = slug
        product.description = sanitized['description']
        product.genre = sanitized['genre']

        uploaded = save_upload(request.files.get('image'))
        if uploaded:
            product.image_url = uploaded

        product.price = float(request.form.get('price', product.price))
        product.stock = int(request.form.get('stock', product.stock))
        product.is_featured = 'is_featured' in request.form
        product.category_id = int(request.form.get('category_id', product.category_id))
        product.vendor_id = int(request.form.get('vendor_id', product.vendor_id)) if request.form.get('vendor_id') else None

        db.session.commit()
        flash('Product updated successfully.', 'success')
        return redirect(url_for('admin.product_list'))

    token = make_token()
    resp = make_response(render_template('admin/product_edit.html',
                          product=product, categories=categories, vendors=vendors,
                          csrf_token=token))
    resp.set_cookie('csrf_token', token, httponly=True, samesite='Lax')
    return resp


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    top_products = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label('total_sold'),
        func.sum(OrderItem.quantity * OrderItem.unit_price).label('revenue')
    ).join(OrderItem, Product.id == OrderItem.product_id
    ).group_by(Product.id
    ).order_by(func.sum(OrderItem.quantity).desc()
    ).limit(10).all()

    total_revenue = db.session.query(
        func.sum(Order.total_amount)
    ).scalar() or 0.0

    total_orders = Order.query.count()
    total_products = Product.query.count()

    revenue_by_genre = db.session.query(
        Product.genre,
        func.sum(OrderItem.quantity * OrderItem.unit_price).label('revenue'),
        func.sum(OrderItem.quantity).label('sold')
    ).join(OrderItem, Product.id == OrderItem.product_id
    ).filter(Product.genre.isnot(None)
    ).group_by(Product.genre
    ).order_by(func.sum(OrderItem.quantity * OrderItem.unit_price).desc()
    ).all()

    revenue_by_category = db.session.query(
        Category.name,
        func.sum(OrderItem.quantity * OrderItem.unit_price).label('revenue'),
        func.sum(OrderItem.quantity).label('sold')
    ).join(Product, Category.id == Product.category_id
    ).join(OrderItem, Product.id == OrderItem.product_id
    ).group_by(Category.id
    ).order_by(func.sum(OrderItem.quantity * OrderItem.unit_price).desc()
    ).all()

    order_status_counts = db.session.query(
        Order.status,
        func.count(Order.id).label('count')
    ).group_by(Order.status).all()

    total_vendors = Vendor.query.count()
    active_vendors = Vendor.query.filter_by(is_active=True).count()

    vendor_revenue = db.session.query(
        Vendor.name,
        func.sum(OrderItem.quantity * OrderItem.unit_price).label('revenue'),
        func.sum(OrderItem.quantity).label('sold')
    ).join(Product, Vendor.id == Product.vendor_id
    ).join(OrderItem, Product.id == OrderItem.product_id
    ).group_by(Vendor.id
    ).order_by(func.sum(OrderItem.quantity * OrderItem.unit_price).desc()
    ).all()

    return render_template('admin/dashboard.html',
                           top_products=[row_to_dict(r) for r in top_products],
                           total_revenue=total_revenue,
                           total_orders=total_orders,
                           total_products=total_products,
                           total_vendors=total_vendors,
                           active_vendors=active_vendors,
                           revenue_by_genre=[row_to_dict(r) for r in revenue_by_genre],
                           revenue_by_category=[row_to_dict(r) for r in revenue_by_category],
                           order_status_counts=[row_to_dict(r) for r in order_status_counts],
                           vendor_revenue=[row_to_dict(r) for r in vendor_revenue])
