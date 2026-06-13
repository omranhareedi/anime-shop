from flask import Blueprint, render_template, session, abort
from app import db
from app.models import Order, Customer

customer_bp = Blueprint('customer', __name__)


@customer_bp.route('/orders')
def order_list():
    user_id = session.get('user_id')
    if not user_id:
        from flask import redirect, url_for, flash
        flash('Please log in to view your orders.', 'warning')
        return redirect(url_for('auth.login', next=url_for('customer.order_list')))

    customer = Customer.query.filter_by(user_id=user_id).first()
    orders = []
    if customer:
        orders = Order.query.filter_by(customer_id=customer.id).order_by(Order.order_date.desc()).all()
    return render_template('customer/orders.html', orders=orders)


@customer_bp.route('/orders/<int:order_id>')
def order_detail(order_id):
    user_id = session.get('user_id')
    if not user_id:
        from flask import redirect, url_for, flash
        flash('Please log in to view your orders.', 'warning')
        return redirect(url_for('auth.login'))

    order = db.session.get(Order, order_id)
    if not order or order.customer.user_id != user_id:
        abort(404)
    return render_template('customer/order_detail.html', order=order)
