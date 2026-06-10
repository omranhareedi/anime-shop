from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models import Order, OrderItem, Customer, Product
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

        order_num = f'ORD-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}-{customer.id}'
        total = 0.0
        order = Order(order_number=order_num, customer_id=customer.id)
        db.session.add(order)
        db.session.flush()

        for product_id, qty in cart.items():
            product = Product.query.get(int(product_id))
            if product:
                item_total = product.price * qty
                total += item_total
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=qty,
                    unit_price=product.price
                )
                db.session.add(order_item)
                product.stock -= qty

        order.total_amount = total
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
