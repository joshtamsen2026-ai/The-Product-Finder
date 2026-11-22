# Product Catalog SQL Practice

Explore a small electronics catalog with SQLite, then export a product-finder
report. The database is created in memory from the sample data in
`product_catalog.py`; it does not persist after the program exits.

## Get started

Requires Python 3.9 or later and the `python-docx` package.

```powershell
python -m pip install -r requirements.txt
python product_finder.py
```

The finder prints the results and generates these files beside the script:

- `product_finder_results.csv` - filterable product details grouped by question.
- `product_finder_results.docx` - formatted answers and inventory summaries.
- `product_finder_results.sql` - queries and results for an existing catalog.

On Windows, the CSV and Word report are opened in their default applications.
Opening may take a few seconds. Each run **overwrites** the generated files;
save any changes to another location before running the script again.

To run the guided filtering and sorting examples instead:

```powershell
python product_queries.py
```

Run the focused checks with:

```powershell
python -m unittest -v test_product_catalog
```

## The five questions

1. Which products are out of stock?
2. Which products have a rating of at least 4.5 and cost under $100?
3. What are the three most expensive accessories?
4. Which products have "Monitor" in their name?
5. Which in-stock products are outside Accessories?

The SQL file is written for **SQLite** and expects an existing `products` table
with the columns defined in `product_catalog.py`. It does not create or populate
the table. The Python scripts create their own temporary catalog.

## Inventory limitations

The catalog contains undated in-stock flags, not unit quantities or sales
transactions. The November 2026 report therefore marks stock quantities,
month-end balances, and units sold as **Not recorded**. It does not infer sales
or historical availability from the stock flags.
