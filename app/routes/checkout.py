from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from app import db
from app.models import Order, OrderItem, Customer, Product
from app.payment import process_payment
from app.security import make_token, sanitize_form_data
from datetime import datetime, timezone

checkout_bp = Blueprint('checkout', __name__)


@checkout_bp.route('/', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('cart.view_cart'))

    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token', '')
        if not csrf_token or csrf_token != session.get('csrf_token'):
            flash('Security token invalid. Please try again.', 'danger')
            return redirect(url_for('checkout.checkout'))

        sanitized = sanitize_form_data(request.form, {
            'first_name': {'max_length': 100},
            'last_name': {'max_length': 100},
            'email': {'type': 'email', 'max_length': 254},
            'phone': {'type': 'phone', 'max_length': 20},
            'address': {'max_length': 500},
            'city': {'max_length': 100},
            'postal_code': {'max_length': 20},
        })

        customer = Customer(
            first_name=sanitized['first_name'],
            last_name=sanitized['last_name'],
            email=sanitized['email'],
            phone=sanitized.get('phone', ''),
            address=sanitized['address'],
            city=sanitized['city'],
            postal_code=sanitized['postal_code'],
            user_id=session.get('user_id'),
        )
        db.session.add(customer)
        db.session.flush()

        total = 0.0
        for product_id, qty in cart.items():
            product = db.session.get(Product, int(product_id))
            if product:
                if product.stock < qty:
                    flash(f'Insufficient stock for "{product.name}" — only {product.stock} available.', 'danger')
                    db.session.rollback()
                    return redirect(url_for('cart.view_cart'))
                total += product.price * qty

        payment_method = request.form.get('payment_method', 'stripe')
        payment_details = {}
        if payment_method == 'stripe':
            payment_details['card_number'] = request.form.get('card_number', '')
            payment_details['card_name'] = request.form.get('card_name', '')
            payment_details['card_expiry'] = request.form.get('card_expiry', '')
            payment_details['card_cvc'] = request.form.get('card_cvc', '')
        elif payment_method == 'paypal':
            payment_details['paypal_email'] = request.form.get('paypal_email', '')
        elif payment_method == 'mobile_money':
            payment_details['mobile_provider'] = request.form.get('mobile_provider', '')
            payment_details['mobile_phone'] = request.form.get('mobile_phone', '')

        result = process_payment(payment_method, total, payment_details)
        if not result.success:
            flash(f'Payment failed: {result.message}', 'danger')
            return redirect(url_for('checkout.checkout'))

        order_num = f'ORD-{datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")}-{customer.id}'
        order = Order(
            order_number=order_num,
            customer_id=customer.id,
            total_amount=total,
            payment_method=payment_method,
            payment_transaction_id=result.transaction_id,
            status='Paid',
        )
        db.session.add(order)
        db.session.flush()

        for product_id, qty in cart.items():
            product = db.session.get(Product, int(product_id))
            if product:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=qty,
                    unit_price=product.price,
                )
                db.session.add(order_item)
                product.stock -= qty

        db.session.commit()
        session.pop('cart', None)
        return redirect(url_for('checkout.confirmation', order_id=order.id))

    items = []
    total = 0.0
    for product_id, qty in cart.items():
        product = db.session.get(Product, int(product_id))
        if product:
            subtotal = product.price * qty
            total += subtotal
            items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})

    session['csrf_token'] = make_token()
    return render_template('checkout.html', items=items, total=total,
                           csrf_token=session['csrf_token'])


@checkout_bp.route('/confirmation/<int:order_id>')
def confirmation(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        abort(404)
    return render_template('confirmation.html', order=order)
