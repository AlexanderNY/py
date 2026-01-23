"""SQL-определения таблиц для SelectCB сервиса."""

# Таблица products
PRODUCTS_TABLE = """
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    product_description VARCHAR(500) NOT NULL
);
"""

# Таблица orders
ORDERS_TABLE = """
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(100) PRIMARY KEY,
    login VARCHAR(255) NOT NULL
);
"""

# Таблица orderdetails
ORDERDETAILS_TABLE = """
CREATE TABLE IF NOT EXISTS orderdetails (
    order_id VARCHAR(100) NOT NULL,
    product_id INTEGER NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);
"""

# Индексы
PRODUCTS_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_products_description ON products(product_description);
"""

ORDERS_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_orders_login ON orders(login);
"""

ORDERDETAILS_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_orderdetails_order_id ON orderdetails(order_id);
CREATE INDEX IF NOT EXISTS idx_orderdetails_product_id ON orderdetails(product_id);
"""

# Все таблицы для инициализации
ALL_TABLES = [
    PRODUCTS_TABLE,
    ORDERS_TABLE,
    ORDERDETAILS_TABLE,
    PRODUCTS_INDEXES,
    ORDERS_INDEXES,
    ORDERDETAILS_INDEXES,
]
