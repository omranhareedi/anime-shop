import secrets
from flask import Flask, g, session
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app(config_class=Config, testing=False):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if testing:
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'test-secret'

    db.init_app(app)

    from app.routes.main import main_bp
    from app.routes.products import products_bp
    from app.routes.cart import cart_bp
    from app.routes.checkout import checkout_bp
    from app.routes.admin import admin_bp
    from app.routes.vendors import vendors_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(checkout_bp, url_prefix='/checkout')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(vendors_bp, url_prefix='/vendors')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.security import configure_session, apply_security_headers, limiter
    configure_session(app)

    with app.app_context():
        from app import models
        db.create_all()

        from app.models import User, Product
        import sqlalchemy as sa
        try:
            db.session.execute(sa.text('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0'))
            db.session.commit()
        except Exception:
            db.session.rollback()

        admin = db.session.query(User).filter_by(username='admin').first()
        if admin:
            if not admin.is_admin:
                admin.is_admin = True
                db.session.commit()
        else:
            admin = User(username='admin', email='admin@narmo.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

        if db.session.query(Product).count() == 0:
            from app.seeds import seed_database
            seed_database()

    @app.before_request
    def security_check():
        g.csp_nonce = secrets.token_hex(16)
        if not limiter.check(limit=120, window=60):
            from flask import abort
            abort(429)

    @app.after_request
    def add_security_headers(response):
        nonce = getattr(g, 'csp_nonce', None)
        return apply_security_headers(response, nonce=nonce)

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template as rt
        return rt('404.html'), 404

    @app.errorhandler(429)
    def ratelimit_handler(e):
        from flask import jsonify
        return jsonify(error='Too many requests. Please slow down.'), 429

    @app.errorhandler(500)
    def server_error(e):
        import traceback
        from flask import jsonify
        tb = traceback.format_exc()
        return jsonify(error='Internal server error', traceback=tb), 500

    @app.context_processor
    def inject_globals():
        from app.models import Category
        try:
            categories = db.session.query(Category).all()
        except Exception:
            categories = []
        return dict(categories=categories, csp_nonce=g.get('csp_nonce', ''),
                    user_id=session.get('user_id'), username=session.get('username'),
                    is_admin=session.get('is_admin', False))

    return app
