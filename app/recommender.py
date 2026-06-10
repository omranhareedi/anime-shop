import re
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from app import db
from app.models import Product, OrderItem, Order
from sqlalchemy import func


def _tokenize(text):
    return set(re.sub(r'[^a-z0-9\s]', '', text.lower()).split())


def _jaccard_similarity(a_tokens, b_tokens):
    union = a_tokens | b_tokens
    if not union:
        return 0.0
    return len(a_tokens & b_tokens) / len(union)


def _tfidf_score(term, doc_set, all_docs_tokenized):
    tf = sum(1 for t in doc_set if t == term) / max(len(doc_set), 1)
    df = sum(1 for d in all_docs_tokenized if term in d)
    idf = math.log((len(all_docs_tokenized) + 1) / (df + 1)) + 1
    return tf * idf


def _cosine_similarity(vec_a, vec_b):
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    na = math.sqrt(sum(v * v for v in vec_a))
    nb = math.sqrt(sum(v * v for v in vec_b))
    if not na or not nb:
        return 0.0
    return dot / (na * nb)


def compute_similarity(product, limit=4):
    all_products = Product.query.filter(Product.id != product.id).all()
    if not all_products:
        return []

    corpus = [p.description or '' for p in [product] + all_products]
    corpus_tokens = [_tokenize(d) for d in corpus]
    vocab = sorted(set(t for doc in corpus_tokens for t in doc))
    vocab_index = {t: i for i, t in enumerate(vocab)}

    def vectorize(tokens):
        counts = Counter(tokens)
        return [_tfidf_score(v, tokens, corpus_tokens) for v in vocab]

    query_vec = vectorize(corpus_tokens[0])

    scored = []
    for i, other in enumerate(all_products):
        other_vec = vectorize(corpus_tokens[i + 1])
        desc_sim = _cosine_similarity(query_vec, other_vec)

        genre_bonus = 0.25 if (product.genre and other.genre and product.genre == other.genre) else 0
        cat_bonus = 0.15 if product.category_id == other.category_id else 0
        name_sim = _jaccard_similarity(
            _tokenize(product.name), _tokenize(other.name)
        ) * 0.1

        score = desc_sim * 0.5 + genre_bonus + cat_bonus + name_sim
        scored.append((score, other))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:limit]


def get_trending(limit=6, days=30):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    results = (
        db.session.query(
            OrderItem.product_id,
            func.sum(OrderItem.quantity).label('qty'),
            func.count(OrderItem.order_id).label('orders'),
        )
        .join(OrderItem.order)
        .filter(OrderItem.order.has(Order.order_date >= cutoff))
        .group_by(OrderItem.product_id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
        .all()
    )
    if not results:
        return Product.query.filter(Product.is_featured == True).limit(limit).all()

    product_ids = [r.product_id for r in results]
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    order_map = {p.id: p for p in products}
    return [order_map[pid] for pid in product_ids if pid in order_map]


def get_genre_affinity(cart_product_ids, limit=6):
    genre_scores = Counter()
    for pid in cart_product_ids:
        product = db.session.get(Product, pid)
        if product and product.genre:
            genre_scores[product.genre] += 1

    if not genre_scores:
        return Product.query.filter(Product.is_featured == True).limit(limit).all()

    weighted = {}
    total = sum(genre_scores.values())
    for genre, count in genre_scores.items():
        weighted[genre] = count / total

    seen_ids = set(cart_product_ids)
    candidates = []
    for genre, weight in weighted.items():
        products = Product.query.filter(
            Product.genre == genre,
            ~Product.id.in_(seen_ids) if seen_ids else True,
        ).all()
        for p in products:
            candidates.append((weight * 0.4 + 0.1, p))
            seen_ids.add(p.id)

    candidates.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in candidates[:limit]]


def get_content_based_recommendations(product, limit=4):
    scored = compute_similarity(product, limit=limit)
    return [p for _, p in scored]


def get_collaborative_recommendations(product_id, limit=4):
    bought_together = (
        db.session.query(
            OrderItem.product_id,
            func.count(OrderItem.order_id).label('frequency'),
        )
        .filter(
            OrderItem.order_id.in_(
                db.session.query(OrderItem.order_id)
                .filter(OrderItem.product_id == product_id)
            ),
            OrderItem.product_id != product_id,
        )
        .group_by(OrderItem.product_id)
        .order_by(func.count(OrderItem.order_id).desc())
        .limit(limit)
        .all()
    )
    if not bought_together:
        return []

    product_ids = [pid for pid, _ in bought_together]
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    order_map = {p.id: p for p in products}
    return [order_map[pid] for pid in product_ids if pid in order_map]


def get_personalized_recommendations(cart_product_ids=None, limit=6):
    if not cart_product_ids:
        return Product.query.filter(Product.is_featured == True).limit(limit).all()

    seen = set(cart_product_ids)
    scored = []

    for pid in cart_product_ids:
        product = db.session.get(Product, pid)
        if not product:
            continue
        collab = get_collaborative_recommendations(pid, limit=3)
        for p in collab:
            if p.id not in seen:
                scored.append((0.6, p))
                seen.add(p.id)
        similar = compute_similarity(product, limit=3)
        for score, p in similar:
            if p.id not in seen:
                scored.append((0.4 + score * 0.2, p))
                seen.add(p.id)

    affinity = get_genre_affinity(cart_product_ids, limit=limit)
    for p in affinity:
        if p.id not in seen:
            scored.append((0.3, p))
            seen.add(p.id)

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:limit]]


def get_popular_all_time(limit=6):
    results = (
        db.session.query(
            OrderItem.product_id,
            func.sum(OrderItem.quantity).label('total_qty'),
        )
        .group_by(OrderItem.product_id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
        .all()
    )
    if not results:
        return Product.query.filter(Product.is_featured == True).limit(limit).all()
    product_ids = [r.product_id for r in results]
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    order_map = {p.id: p for p in products}
    return [order_map[pid] for pid in product_ids if pid in order_map]
