"""Create the sample electronics catalog used by both SQL exercises."""

import sqlite3
from textwrap import dedent

PRODUCTS = (
    ("Wireless Mouse", "Accessories", 29.99, 4.5, 1),
    ("Mechanical Keyboard", "Accessories", 89.99, 4.8, 1),
    ("USB-C Hub", "Accessories", 34.99, 4.2, 0),
    ("27-inch Monitor", "Displays", 299.99, 4.6, 1),
    ("24-inch Monitor", "Displays", 179.99, 4.3, 1),
    ("Webcam HD", "Accessories", 49.99, 3.9, 1),
    ("Noise-Canceling Headphones", "Audio", 199.99, 4.7, 1),
    ("Bluetooth Speaker", "Audio", 59.99, 4.1, 0),
    ("Laptop Stand", "Accessories", 39.99, 4.4, 1),
    ("External SSD 1TB", "Storage", 89.99, 4.6, 1),
    ("External SSD 2TB", "Storage", 149.99, 4.5, 1),
    ("Flash Drive 64GB", "Storage", 12.99, 4.0, 1),
)


def create_database() -> sqlite3.Connection:
    """Create and populate a temporary SQLite catalog; the caller closes it."""
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute(dedent("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                rating REAL,
                in_stock INTEGER DEFAULT 1
            )
        """))
        connection.executemany("""
            INSERT INTO products (name, category, price, rating, in_stock)
            VALUES (?, ?, ?, ?, ?)
        """, PRODUCTS)
        connection.commit()
    except sqlite3.Error:
        connection.close()
        raise
    return connection
