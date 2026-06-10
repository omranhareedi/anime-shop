from app import db
from app.models import Product, OrderItem
from collections import Counter
from sqlalchemy import func


def get_content_based_recommendations(product, limit=4):
    same_genre = Product.query.filter(
        Product.genre == product.genre,
        Product.id != product.id
    ).limit(limit).all()

    if len(same_genre) >= limit:
        return same_genre[:limit]

    same_category = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        ~Product.genre.in_([product.genre] if product.genre else [])
    ).limit(limit - len(same_genre)).all()

    return same_genre + same_category


def get_collaborative_recommendations(product_id, limit=4):
    bought_together = (
        db.session.query(
            OrderItem.product_id,
            func.count(OrderItem.order_id).label('frequency')
        )
        .filter(
            OrderItem.order_id.in_(
                db.session.query(OrderItem.order_id)
                .filter(OrderItem.product_id == product_id)
            ),
            OrderItem.product_id != product_id
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
    if cart_product_ids:
        all_recs = []
        seen_ids = set(cart_product_ids)

        for pid in cart_product_ids:
            product = Product.query.get(pid)
            if product:
                collab = get_collaborative_recommendations(pid, limit=2)
                for p in collab:
                    if p.id not in seen_ids:
                        all_recs.append(p)
                        seen_ids.add(p.id)

                content = get_content_based_recommendations(product, limit=2)
                for p in content:
                    if p.id not in seen_ids:
                        all_recs.append(p)
                        seen_ids.add(p.id)

            if len(all_recs) >= limit:
                break

        if len(all_recs) >= limit:
            return all_recs[:limit]

        genre_counts = Counter()
        for pid in cart_product_ids:
            product = Product.query.get(pid)
            if product and product.genre:
                genre_counts[product.genre] += 1

        if genre_counts:
            top_genre = genre_counts.most_common(1)[0][0]
            genre_recs = Product.query.filter(
                Product.genre == top_genre,
                ~Product.id.in_(seen_ids)
            ).limit(limit - len(all_recs)).all()
            all_recs.extend(genre_recs)

        return all_recs[:limit]

    return Product.query.filter(Product.is_featured == True).limit(limit).all()
