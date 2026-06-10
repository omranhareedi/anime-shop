from flask import Blueprint, render_template
from app import db
from app.models import Product, Order, OrderItem, Category
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)


def row_to_dict(row):
    return {key: getattr(row, key) for key in row._fields}


@admin_bp.route('/dashboard')
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

    return render_template('admin/dashboard.html',
                           top_products=[row_to_dict(r) for r in top_products],
                           total_revenue=total_revenue,
                           total_orders=total_orders,
                           total_products=total_products,
                           revenue_by_genre=[row_to_dict(r) for r in revenue_by_genre],
                           revenue_by_category=[row_to_dict(r) for r in revenue_by_category],
                           order_status_counts=[row_to_dict(r) for r in order_status_counts])
