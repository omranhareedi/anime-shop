-- ============================================================
-- Otaku Haven - Anime & Pop Culture Shop
-- Database Schema (PostgreSQL compatible)
-- Generated for Final Project Submission
-- ============================================================

-- Categories table: groups products by type
CREATE TABLE IF NOT EXISTS categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(80)  NOT NULL UNIQUE,
    slug        VARCHAR(80)  NOT NULL UNIQUE,
    description TEXT
);

-- Products table: core inventory with pricing and metadata
CREATE TABLE IF NOT EXISTS products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    slug        VARCHAR(200) NOT NULL UNIQUE,
    description TEXT,
    price       FLOAT        NOT NULL CHECK (price >= 0),
    image_url   VARCHAR(300) DEFAULT 'default.jpg',
    stock       INTEGER      NOT NULL DEFAULT 0 CHECK (stock >= 0),
    is_featured BOOLEAN      DEFAULT FALSE,
    genre       VARCHAR(100),
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    category_id INTEGER     NOT NULL REFERENCES categories(id) ON DELETE CASCADE
);

-- Customers table: captures checkout information
CREATE TABLE IF NOT EXISTS customers (
    id          SERIAL PRIMARY KEY,
    first_name  VARCHAR(100) NOT NULL,
    last_name   VARCHAR(100) NOT NULL,
    email       VARCHAR(200) NOT NULL,
    phone       VARCHAR(20),
    address     TEXT         NOT NULL,
    city        VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20)  NOT NULL,
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- Orders table: one per checkout transaction
CREATE TABLE IF NOT EXISTS orders (
    id           SERIAL PRIMARY KEY,
    order_number VARCHAR(20) NOT NULL UNIQUE,
    order_date   TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    total_amount FLOAT       NOT NULL DEFAULT 0.0 CHECK (total_amount >= 0),
    status       VARCHAR(20) NOT NULL DEFAULT 'Pending',
    customer_id  INTEGER     NOT NULL REFERENCES customers(id) ON DELETE CASCADE
);

-- Order Items table: line items within an order
CREATE TABLE IF NOT EXISTS order_items (
    id         SERIAL PRIMARY KEY,
    order_id   INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity   INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    unit_price FLOAT   NOT NULL CHECK (unit_price >= 0)
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_genre     ON products(genre);
CREATE INDEX IF NOT EXISTS idx_orders_customer    ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order   ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);
