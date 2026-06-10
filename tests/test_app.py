import pytest
from app import create_app, db
from app.models import Product, Category, Customer, Order, OrderItem, Vendor
from app.seeds import seed_database


@pytest.fixture
def app():
    app = create_app(testing=True)

    with app.app_context():
        db.create_all()
        seed_database()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


def test_homepage(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'Narmo' in resp.data


def test_product_listing(client):
    resp = client.get('/products/')
    assert resp.status_code == 200
    assert b'Naruto' in resp.data


def test_product_detail(client):
    resp = client.get('/products/naruto-sage-mode-figure')
    assert resp.status_code == 200
    assert b'Sage Mode' in resp.data


def test_category_filter(client):
    resp = client.get('/products/?category=figures')
    assert resp.status_code == 200
    assert b'Figures' in resp.data


def test_cart_empty(client):
    resp = client.get('/cart/')
    assert resp.status_code == 200
    assert b'empty' in resp.data or b'Empty' in resp.data


def test_add_to_cart(client):
    with client.session_transaction() as sess:
        sess['cart'] = {}

    resp = client.post('/cart/add', data={'product_id': 1, 'quantity': 2})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'ok'


def test_cart_with_items(client):
    with client.session_transaction() as sess:
        sess['cart'] = {'1': 2, '3': 1}

    resp = client.get('/cart/')
    assert resp.status_code == 200


def test_checkout_page(client):
    with client.session_transaction() as sess:
        sess['cart'] = {'1': 1}

    resp = client.get('/checkout/')
    assert resp.status_code == 200


def test_checkout_submit_stripe(client):
    with client.session_transaction() as sess:
        sess['cart'] = {'1': 1}

    resp = client.post('/checkout/', data={
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'address': '123 Anime St',
        'city': 'Akihabara',
        'postal_code': '100-0001',
        'payment_method': 'stripe',
        'card_number': '4242 4242 4242 4242',
        'card_name': 'Test User',
        'card_expiry': '12/28',
        'card_cvc': '123',
    })
    assert resp.status_code == 302


def test_checkout_submit_paypal(client):
    with client.session_transaction() as sess:
        sess['cart'] = {'1': 1}

    resp = client.post('/checkout/', data={
        'first_name': 'Jane',
        'last_name': 'Doe',
        'email': 'jane@example.com',
        'address': '456 Manga Ln',
        'city': 'Shinjuku',
        'postal_code': '160-0022',
        'payment_method': 'paypal',
        'paypal_email': 'jane@paypal.com',
    })
    assert resp.status_code == 302


def test_checkout_submit_momo(client):
    with client.session_transaction() as sess:
        sess['cart'] = {'1': 1}

    resp = client.post('/checkout/', data={
        'first_name': 'Kojo',
        'last_name': 'Asamoah',
        'email': 'kojo@example.com',
        'address': '789 High St',
        'city': 'Accra',
        'postal_code': 'GA-100',
        'payment_method': 'mobile_money',
        'mobile_provider': 'mtn',
        'mobile_phone': '0551234567',
    })
    assert resp.status_code == 302


def test_checkout_payment_failure(client):
    with client.session_transaction() as sess:
        sess['cart'] = {'1': 1}

    resp = client.post('/checkout/', data={
        'first_name': 'Bad',
        'last_name': 'Card',
        'email': 'bad@example.com',
        'address': '1 Broken St',
        'city': 'Nowhere',
        'postal_code': '00000',
        'payment_method': 'stripe',
        'card_number': '123',
        'card_name': '',
        'card_expiry': '',
        'card_cvc': '',
    })
    assert resp.status_code == 302


def test_admin_dashboard(client):
    resp = client.get('/admin/dashboard')
    assert resp.status_code == 200
    assert b'Admin' in resp.data


def test_recommendation_api(client):
    resp = client.get('/products/api/recommendations?genre=Action&limit=3')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) <= 3


def test_models():
    assert hasattr(Category, 'products')
    assert hasattr(Product, 'category')
    assert hasattr(Customer, 'orders')
    assert hasattr(Order, 'items')
    assert hasattr(Order, 'payment_method')
    assert hasattr(Order, 'payment_transaction_id')
    assert hasattr(OrderItem, 'product')


def test_payment_stripe_success(app):
    from app.payment import process_payment
    result = process_payment('stripe', 49.99, {'card_number': '4242 4242 4242 4242'})
    assert result.success
    assert result.transaction_id.startswith('stripe_')


def test_payment_stripe_failure(app):
    from app.payment import process_payment
    result = process_payment('stripe', 49.99, {'card_number': ''})
    assert not result.success


def test_payment_paypal_success(app):
    from app.payment import process_payment
    result = process_payment('paypal', 29.99, {'paypal_email': 'user@paypal.com'})
    assert result.success
    assert result.transaction_id.startswith('paypal_')


def test_payment_paypal_failure(app):
    from app.payment import process_payment
    result = process_payment('paypal', 29.99, {'paypal_email': 'notanemail'})
    assert not result.success


def test_payment_momo_success(app):
    from app.payment import process_payment
    result = process_payment('mobile_money', 15.00, {'mobile_provider': 'mtn', 'mobile_phone': '0551234567'})
    assert result.success
    assert result.transaction_id.startswith('momo_')


def test_payment_momo_failure(app):
    from app.payment import process_payment
    result = process_payment('mobile_money', 15.00, {'mobile_provider': 'vodafone', 'mobile_phone': '0551234567'})
    assert not result.success


def test_payment_unsupported_gateway(app):
    from app.payment import process_payment
    result = process_payment('bitcoin', 99.99, {})
    assert not result.success


def test_trending_api(client):
    resp = client.get('/products/api/recommendations?method=trending&limit=3')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) <= 3


def test_popular_api(client):
    resp = client.get('/products/api/recommendations?method=popular&limit=3')
    assert resp.status_code == 200


def test_recommender_compute_similarity(app):
    with app.app_context():
        from app.recommender import compute_similarity
        product = Product.query.first()
        scored = compute_similarity(product, limit=3)
        assert len(scored) <= 3
        if scored:
            score, other = scored[0]
            assert 0 <= score <= 1


def test_recommender_get_trending(app):
    with app.app_context():
        from app.recommender import get_trending
        results = get_trending(limit=3)
        assert len(results) <= 3


def test_recommender_genre_affinity(app):
    with app.app_context():
        from app.recommender import get_genre_affinity
        results = get_genre_affinity([1], limit=3)
        assert len(results) <= 3


def test_security_headers(client):
    resp = client.get('/')
    assert resp.headers.get('X-Content-Type-Options') == 'nosniff'
    assert resp.headers.get('X-Frame-Options') == 'DENY'
    assert resp.headers.get('X-XSS-Protection') == '1; mode=block'
    assert resp.headers.get('Referrer-Policy') == 'strict-origin-when-cross-origin'
    assert 'Content-Security-Policy' in resp.headers
    assert 'default-src' in resp.headers['Content-Security-Policy']


def test_security_csp_nonce(client):
    resp = client.get('/')
    csp = resp.headers.get('Content-Security-Policy', '')
    assert 'nonce-' in csp
    html = resp.data.decode()
    assert 'nonce="' in html


def test_security_rate_limit(client):
    from app.security import sanitize_input, sanitize_email, make_token
    assert sanitize_input('<script>alert(1)</script>') == '&lt;script&gt;alert(1)&lt;/script&gt;'
    assert sanitize_email(' UPPER@Me.COM ') == 'upper@me.com'
    assert len(make_token()) == 32


def test_security_sanitize_length(client):
    from app.security import sanitize_input
    long = 'a' * 1000
    assert len(sanitize_input(long, max_length=10)) == 10


def test_vendor_list(client):
    resp = client.get('/vendors/')
    assert resp.status_code == 200
    assert b'OtakuCraft' in resp.data or b'Vendors' in resp.data


def test_vendor_store(client):
    resp = client.get('/vendors/otakucraft')
    assert resp.status_code == 200
    assert b'OtakuCraft' in resp.data


def test_vendor_store_not_found(client):
    resp = client.get('/vendors/nonexistent-vendor')
    assert resp.status_code == 404


def test_vendor_register_page(client):
    resp = client.get('/vendors/register')
    assert resp.status_code == 200
    assert b'Open Your Store' in resp.data or b'Vendor' in resp.data


def test_vendor_register_submit(client):
    resp = client.post('/vendors/register', data={
        'name': 'TestVendor',
        'email': 'test@vendor.com',
        'description': 'A test vendor store.',
        'location': 'Test City',
    })
    assert resp.status_code == 302
    assert '/vendors/testvendor' in resp.location


def test_vendor_model(app):
    with app.app_context():
        vendor = Vendor.query.filter_by(slug='otakucraft').first()
        assert vendor is not None
        assert hasattr(vendor, 'products')
        assert len(vendor.products) > 0


def test_product_has_vendor(app):
    with app.app_context():
        product = Product.query.first()
        assert hasattr(product, 'vendor')


def test_checkout_csrf_protection(client):
    with client.session_transaction() as sess:
        sess['cart'] = {'1': 1}
    resp = client.post('/checkout/', data={
        'first_name': 'Hacker',
        'last_name': 'Bad',
        'email': 'x@x.com',
        'address': 'x',
        'city': 'x',
        'postal_code': 'x',
        'payment_method': 'stripe',
        'card_number': '4242 4242 4242 4242',
    })
    assert resp.status_code == 302
    assert '/checkout/' in resp.location


def test_recommender_popular_all_time(app):
    with app.app_context():
        from app.recommender import get_popular_all_time
        results = get_popular_all_time(limit=3)
        assert len(results) <= 3


def test_admin_product_list(client):
    resp = client.get('/admin/products')
    assert resp.status_code == 200
    assert b'Naruto' in resp.data


def test_admin_product_edit_page(client):
    resp = client.get('/admin/products/1/edit')
    assert resp.status_code == 200
    assert b'Sage Mode' in resp.data or b'Edit' in resp.data


def test_search_results(client):
    resp = client.get('/products/?q=Naruto')
    assert resp.status_code == 200
    assert b'Naruto' in resp.data

def test_search_no_results(client):
    resp = client.get('/products/?q=xyznonexistent')
    assert resp.status_code == 200
    assert b'No matches' in resp.data


def test_admin_product_edit_submit(client):
    resp = client.get('/admin/products/1/edit')
    csrf_token = resp.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
    client.set_cookie('csrf_token', csrf_token)
    resp = client.post('/admin/products/1/edit', data={
        'csrf_token': csrf_token,
        'name': 'Naruto Sage Mode Figure - Updated',
        'price': '54.99',
        'stock': '20',
        'category_id': '1',
        'vendor_id': '1',
        'description': 'Updated description.',
        'genre': 'Action',
        'image_url': 'naruto_updated.jpg',
        'is_featured': 'on',
    })
    assert resp.status_code == 302
    assert '/admin/products' in resp.location

    with client.application.app_context():
        p = Product.query.get(1)
        assert p.name == 'Naruto Sage Mode Figure - Updated'
        assert p.price == 54.99
        assert p.stock == 20


def test_admin_product_edit_not_found(client):
    resp = client.get('/admin/products/999/edit')
    assert resp.status_code == 404
