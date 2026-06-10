from flask import Blueprint, render_template, request, jsonify, session
from app import db
from app.models import Product

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('/preview')
def cart_preview():
    cart = session.get('cart', {})
    items = []
    total = 0.0
    count = 0
    for product_id, quantity in cart.items():
        product = db.session.get(Product, int(product_id))
        if product:
            subtotal = product.price * quantity
            total += subtotal
            count += quantity
            items.append({'id': product.id, 'name': product.name[:40],
                          'image': product.image_url, 'price': product.price,
                          'quantity': quantity, 'subtotal': round(subtotal, 2)})
    return jsonify({'items': items[:5], 'total': round(total, 2), 'count': count})


@cart_bp.route('/count')
def cart_count():
    cart = session.get('cart', {})
    return jsonify({'count': sum(cart.values())})


@cart_bp.route('/')
def view_cart():
    cart = session.get('cart', {})
    items = []
    total = 0.0
    for product_id, quantity in cart.items():
        product = db.session.get(Product, int(product_id))
        if product:
            subtotal = product.price * quantity
            total += subtotal
            items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
    return render_template('cart.html', items=items, total=total)


@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    product_id = str(request.form.get('product_id'))
    quantity = int(request.form.get('quantity', 1))
    cart = session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + quantity
    session['cart'] = cart
    return jsonify({'status': 'ok', 'cart_count': sum(cart.values())})


@cart_bp.route('/update', methods=['POST'])
def update_cart():
    product_id = str(request.form.get('product_id'))
    quantity = int(request.form.get('quantity'))
    cart = session.get('cart', {})
    if quantity <= 0:
        cart.pop(product_id, None)
    else:
        cart[product_id] = quantity
    session['cart'] = cart
    total = 0.0
    for pid, qty in cart.items():
        product = db.session.get(Product, int(pid))
        if product:
            total += product.price * qty
    return jsonify({'status': 'ok', 'cart_count': sum(cart.values()), 'total': round(total, 2)})


@cart_bp.route('/remove', methods=['POST'])
def remove_from_cart():
    product_id = str(request.form.get('product_id'))
    cart = session.get('cart', {})
    cart.pop(product_id, None)
    session['cart'] = cart
    return jsonify({'status': 'ok', 'cart_count': sum(cart.values())})
