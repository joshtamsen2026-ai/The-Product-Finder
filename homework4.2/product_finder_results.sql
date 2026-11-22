-- Run these queries against an existing SQLite products table.

-- 1. Which products are out of stock?
SELECT name, category
FROM products
WHERE in_stock = 0;
-- Results: name | category
-- USB-C Hub | Accessories
-- Bluetooth Speaker | Audio

-- 2. Which products have a rating of 4.5 or higher AND cost less than $100?
SELECT name, rating, price
FROM products
WHERE rating >= 4.5 AND price < 100.00;
-- Results: name | rating | price
-- Wireless Mouse | 4.5 | 29.99
-- Mechanical Keyboard | 4.8 | 89.99
-- External SSD 1TB | 4.6 | 89.99

-- 3. What are the 3 most expensive products in the "Accessories" category?
SELECT name, price
FROM products
WHERE category = 'Accessories'
ORDER BY price DESC
LIMIT 3;
-- Results: name | price
-- Mechanical Keyboard | 89.99
-- Webcam HD | 49.99
-- Laptop Stand | 39.99

-- 4. Which products have "Monitor" in their name?
SELECT *
FROM products
WHERE name LIKE '%Monitor%';
-- Results: id | name | category | price | rating | in_stock
-- 4 | 27-inch Monitor | Displays | 299.99 | 4.6 | 1
-- 5 | 24-inch Monitor | Displays | 179.99 | 4.3 | 1

-- 5. Which products are NOT in the "Accessories" category and are in stock?
SELECT name, category, price
FROM products
WHERE category != 'Accessories' AND in_stock = 1
ORDER BY category, price;
-- Results: name | category | price
-- Noise-Canceling Headphones | Audio | 199.99
-- 24-inch Monitor | Displays | 179.99
-- 27-inch Monitor | Displays | 299.99
-- Flash Drive 64GB | Storage | 12.99
-- External SSD 1TB | Storage | 89.99
-- External SSD 2TB | Storage | 149.99
