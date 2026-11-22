"""Demonstrate fundamental SQL queries against the sample product catalog."""

from product_catalog import create_database


def main() -> None:
    """Run the catalog exercise."""
    ## Set up the shared in-memory catalog.
    connection = create_database()
    cursor = connection.cursor()

    ## Demonstrate filtering, matching, sorting, and limits.
    print("=== Products Under $50 ===")
    cursor.execute("SELECT name, price FROM products WHERE price < 50.00")
    for row in cursor.fetchall():
        print(f"  {row[0]}: ${row[1]:.2f}")

    print("\n=== In-Stock Accessories Under $50 ===")
    cursor.execute("""
        SELECT name, price, rating
        FROM products
        WHERE category = 'Accessories'
          AND price < 50.00
          AND in_stock = 1
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: ${row[1]:.2f} (Rating: {row[2]})")

    print("\n=== SSD Products ===")
    cursor.execute("SELECT name, price FROM products WHERE name LIKE '%SSD%'")
    for row in cursor.fetchall():
        print(f"  {row[0]}: ${row[1]:.2f}")

    print("\n=== Audio & Storage Products ===")
    cursor.execute("""
        SELECT name, category, price
        FROM products
        WHERE category IN ('Audio', 'Storage')
    """)
    for row in cursor.fetchall():
        print(f"  [{row[1]}] {row[0]}: ${row[2]:.2f}")

    print("\n=== Top 5 by Rating ===")
    cursor.execute("""
        SELECT name, rating, price
        FROM products
        WHERE in_stock = 1
        ORDER BY rating DESC, price DESC
        LIMIT 5
    """)
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"  {i}. {row[0]} — Rating: {row[1]}, ${row[2]:.2f}")

    print("\n=== 3 Cheapest Products ===")
    cursor.execute("""
        SELECT name, price
        FROM products
        ORDER BY price ASC
        LIMIT 3
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: ${row[1]:.2f}")

    print("\n=== Mid-Range In-Stock Products ===")
    cursor.execute("""
        SELECT name, category, price
        FROM products
        WHERE price BETWEEN 50.00 AND 200.00
          AND in_stock = 1
        ORDER BY price
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]} ({row[1]}): ${row[2]:.2f}")

    connection.close()


if __name__ == "__main__":
    main()
