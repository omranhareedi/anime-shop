# Narmo — Attack on Titan Themed Anime Marketplace

A Flask-based multi-vendor e-commerce marketplace for anime merchandise, themed after Attack on Titan. Built for the **45/45 final project** rubric.

## Features

- **Multi-vendor** — 4 vendors with ratings and store pages
- **Product catalog** — 12 products across 5 categories, search, filter by category/genre
- **AI recommendations** — TF-IDF similarity, trending, popular, collaborative filtering
- **Cart & checkout** — AJAX cart, payment via Stripe/PayPal/Mobile Money
- **Admin dashboard** — Analytics with Chart.js, product CRUD with image upload
- **User auth** — Register/login, admin auto-redirect, `admin_required` decorator
- **Dark mode** — Toggle with `prefers-color-scheme` detection and localStorage
- **Pagination** — 12 products per page, configurable
- **Security** — CSP nonces, rate limiting, CSRF, input sanitization, security headers
- **Full AoT theme** — Survey Corps teal/gold palette, "Shinzou wo Sasageyo!" hero

## Tech Stack

- **Backend**: Python 3.11+, Flask, SQLAlchemy, WTForms
- **Frontend**: Bootstrap 5, Chart.js, custom CSS/JS
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Container**: Docker + docker-compose
- **CI/CD**: GitHub Actions (lint, test, build)

## Quick Start

```bash
# Clone and enter
git clone <repo-url>
cd anime-shop

# Create venv and install deps
python -m venv .venv
.\.venv\Scripts\activate    # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Delete DB to force fresh seed (optional)
rm instance/anime_shop.db

# Run
python run.py
```

Visit **http://localhost:5000**

### Admin Login

- **Username**: `admin`
- **Password**: `admin123`

## Docker

```bash
docker compose up --build
```

## Tests

```bash
pytest tests/test_app.py -v
```

## Project Structure

```
anime-shop/
├── app/
│   ├── __init__.py        # App factory, blueprints, security middleware
│   ├── models.py          # 7 SQLAlchemy models + decorators
│   ├── seeds.py           # Seed data (12 products, 4 vendors, admin)
│   ├── routes/            # Blueprints: main, products, cart, checkout, admin, vendors, auth
│   ├── static/            # CSS, JS, images
│   ├── templates/         # Jinja2 templates (18+ pages)
│   ├── recommender.py     # AI recommendation engine
│   ├── payment.py         # Stripe/PayPal/MoMo gateways
│   └── security.py        # CSP, rate limiter, sanitization
├── database/
│   └── schema.sql         # PostgreSQL DDL
├── .github/workflows/     # CI/CD pipeline
├── Dockerfile
├── docker-compose.yml
├── docker-evidence.txt    # Build evidence for submission
└── requirements.txt
```
