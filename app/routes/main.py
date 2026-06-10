from flask import Blueprint, render_template, session
from app.models import Product, Category
from app.recommender import (
    get_personalized_recommendations, get_trending,
    get_popular_all_time
)

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    featured = Product.query.filter_by(is_featured=True).limit(6).all()
    categories = Category.query.all()
    trending = get_trending(limit=4)

    cart_items = list(session.get('cart', {}).keys())
    rec_product_ids = [int(x) for x in cart_items] if cart_items else []
    recommendations = get_personalized_recommendations(
        cart_product_ids=rec_product_ids if rec_product_ids else None,
        limit=4
    )

    return render_template('index.html', featured=featured,
                           categories=categories,
                           recommendations=recommendations,
                           trending=trending)
