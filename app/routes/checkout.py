from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models import Order, OrderItem, Customer, Product
from app.payment import process_payment
from datetime import datetime

checkout_bp = Blueprint('checkout', __name__)


@checkout_bp.route('/', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('cart.view_cart'))

    if request.method == 'POST':
        customer = Customer(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            email=request.form['email'],
            phone=request.form.get('phone', ''),
            address=request.form['address'],
            city=request.form['city'],
            postal_code=request.form['postal_code'],
        )
        db.session.add(customer)
        db.session.flush()

        total = 0.0
        for product_id, qty in cart.items():
            product = Product.query.get(int(product_id))
            if product:
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

        order_num = f'ORD-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}-{customer.id}'
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
            product = Product.query.get(int(product_id))
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
        product = Product.query.get(int(product_id))
        if product:
            subtotal = product.price * qty
            total += subtotal
            items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})

    return render_template('checkout.html', items=items, total=total)


@checkout_bp.route('/confirmation/<int:order_id>')
def confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('confirmation.html', order=order)
