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
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_homepage(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'Otaku Haven' in resp.data


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


def test_checkout_submit(client):
    with client.session_transaction() as sess:
        sess['cart'] = {'1': 1}

    resp = client.post('/checkout/', data={
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'address': '123 Anime St',
        'city': 'Akihabara',
        'postal_code': '100-0001',
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
    assert hasattr(OrderItem, 'product')
