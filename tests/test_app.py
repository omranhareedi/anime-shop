import pytest
from app import create_app, db
from app.models import Product, Category, Customer, Order, OrderItem
from app.seeds import seed_database


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

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
