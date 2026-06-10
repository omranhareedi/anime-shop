from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import Vendor, Product
from app.security import make_token, sanitize_form_data

vendors_bp = Blueprint('vendors', __name__)


@vendors_bp.route('/')
def vendor_list():
    vendors = Vendor.query.filter_by(is_active=True).all()
    for v in vendors:
        v.product_count = Product.query.filter_by(vendor_id=v.id).count()
    return render_template('vendors/list.html', vendors=vendors)


@vendors_bp.route('/<slug>')
def vendor_store(slug):
    vendor = Vendor.query.filter_by(slug=slug, is_active=True).first_or_404()
    products = Product.query.filter_by(vendor_id=vendor.id).all()
    return render_template('vendors/store.html', vendor=vendor, products=products)


@vendors_bp.route('/register', methods=['GET', 'POST'])
def vendor_register():
    if request.method == 'POST':
        sanitized = sanitize_form_data(request.form, {
            'name': {'max_length': 120},
            'email': {'type': 'email', 'max_length': 254},
            'description': {'max_length': 1000},
            'location': {'max_length': 200},
        })
        slug = sanitized['name'].lower().replace(' ', '-')[:120]
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')

        existing = Vendor.query.filter_by(slug=slug).first()
        if existing:
            flash('A vendor with this name already exists.', 'danger')
            return render_template('vendors/register.html')

        vendor = Vendor(
            name=sanitized['name'],
            slug=slug,
            email=sanitized['email'],
            description=sanitized.get('description', ''),
            location=sanitized.get('location', ''),
            is_active=True,
        )
        db.session.add(vendor)
        db.session.commit()
        flash(f'Welcome, {vendor.name}! Your store is now live.', 'success')
        return redirect(url_for('vendors.vendor_store', slug=vendor.slug))

    return render_template('vendors/register.html')
