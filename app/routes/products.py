from flask import Blueprint, render_template, request, jsonify
from app.models import Product, Category
from app.recommender import get_content_based_recommendations, get_collaborative_recommendations, get_personalized_recommendations

products_bp = Blueprint('products', __name__)


@products_bp.route('/')
def product_list():
    category_slug = request.args.get('category')
    genre = request.args.get('genre')
    query = Product.query

    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            query = query.filter_by(category_id=cat.id)

    if genre:
        query = query.filter_by(genre=genre)

    products = query.all()
    categories = Category.query.all()
    genres = ['Action', 'Adventure', 'Comedy', 'Sci-Fi', 'Fantasy']
    return render_template('products.html', products=products,
                           categories=categories, genres=genres,
                           current_category=category_slug, current_genre=genre)


@products_bp.route('/api/recommendations', methods=['GET'])
def api_recommendations():
    genre = request.args.get('genre')
    product_id = request.args.get('product_id')
    limit = int(request.args.get('limit', 6))

    if product_id:
        product = Product.query.get(int(product_id))
        if product:
            recs = get_collaborative_recommendations(product.id, limit=limit)
            if not recs:
                recs = get_content_based_recommendations(product, limit=limit)
        else:
            recs = Product.query.limit(limit).all()
    elif genre:
        recs = Product.query.filter_by(genre=genre).limit(limit).all()
    else:
        recs = Product.query.filter_by(is_featured=True).limit(limit).all()

    return jsonify([{
        'id': p.id,
        'name': p.name,
        'slug': p.slug,
        'price': p.price,
        'image': p.image_url,
        'genre': p.genre,
        'category': p.category.name
    } for p in recs])


@products_bp.route('/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    content_recs = get_content_based_recommendations(product, limit=4)
    collab_recs = get_collaborative_recommendations(product.id, limit=4)
    return render_template('product_detail.html', product=product,
                           related=content_recs, collab_recs=collab_recs)
