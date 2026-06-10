from flask import Blueprint, render_template, request, jsonify, session, current_app
from app import db
from app.models import Product, Category
from app.recommender import (
    get_content_based_recommendations, get_collaborative_recommendations,
    get_personalized_recommendations, compute_similarity,
    get_trending, get_genre_affinity, get_popular_all_time
)

products_bp = Blueprint('products', __name__)


@products_bp.route('/')
def product_list():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('PRODUCTS_PER_PAGE', 12)
    category_slug = request.args.get('category')
    genre = request.args.get('genre')
    search = request.args.get('q', '').strip()
    query = Product.query

    if category_slug:
        cat = db.session.query(Category).filter_by(slug=category_slug).first()
        if cat:
            query = query.filter_by(category_id=cat.id)

    if genre:
        query = query.filter_by(genre=genre)

    if search:
        like = f'%{search}%'
        query = query.filter(
            Product.name.ilike(like) |
            Product.description.ilike(like) |
            Product.genre.ilike(like)
        )

    products = query.paginate(page=page, per_page=per_page, error_out=False)
    categories = db.session.query(Category).all()
    genres = ['Action', 'Adventure', 'Comedy', 'Sci-Fi', 'Fantasy']
    return render_template('products.html', products=products,
                           categories=categories, genres=genres,
                           current_category=category_slug, current_genre=genre,
                           search=search)


@products_bp.route('/api/recommendations', methods=['GET'])
def api_recommendations():
    method = request.args.get('method', 'hybrid')
    genre = request.args.get('genre')
    product_id = request.args.get('product_id')
    limit = int(request.args.get('limit', 6))

    if product_id:
        product = db.session.get(Product, int(product_id))
        if product:
            recs = get_collaborative_recommendations(product.id, limit=limit)
            if not recs:
                recs = get_content_based_recommendations(product, limit=limit)
        else:
            recs = Product.query.limit(limit).all()
    elif genre:
        recs = Product.query.filter_by(genre=genre).limit(limit).all()
    elif method == 'trending':
        recs = get_trending(limit=limit)
    elif method == 'popular':
        recs = get_popular_all_time(limit=limit)
    else:
        cart = session.get('cart', {})
        cart_ids = [int(k) for k in cart.keys()] if cart else None
        recs = get_personalized_recommendations(cart_product_ids=cart_ids, limit=limit)

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
    viewed = session.get('recently_viewed', [])
    viewed = [v for v in viewed if v != product.id]
    viewed.insert(0, product.id)
    session['recently_viewed'] = viewed[:8]
    content_recs = get_content_based_recommendations(product, limit=4)
    collab_recs = get_collaborative_recommendations(product.id, limit=4)
    scored = compute_similarity(product, limit=6)
    return render_template('product_detail.html', product=product,
                           related=content_recs, collab_recs=collab_recs,
                           ai_scores=[(p, round(s * 100)) for s, p in scored])
