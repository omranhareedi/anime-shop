from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from app.routes.main import main_bp
    from app.routes.products import products_bp
    from app.routes.cart import cart_bp
    from app.routes.checkout import checkout_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(checkout_bp, url_prefix='/checkout')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        from app import models
        db.create_all()
        from app.models import Product
        if Product.query.count() == 0:
            from app.seeds import seed_database
            seed_database()

    @app.context_processor
    def inject_globals():
        from app.models import Category
        try:
            categories = Category.query.all()
        except Exception:
            categories = []
        return dict(categories=categories)

    return app
