"""Query a sample product catalog and export CSV, SQL, and Word reports."""

import csv
import os
from pathlib import Path
from textwrap import dedent
from typing import Any

from product_catalog import create_database

try:
    Document = __import__("docx", fromlist=["Document"]).Document
except ImportError:
    Document = None

NOT_RECORDED = "Not recorded"
NO_PRODUCTS = "No products"

Result = tuple[str, tuple[str, ...], list[tuple[Any, ...]]]
Catalog = list[tuple[Any, ...]]
FIELD_LABELS = {
    "name": "Product Name",
    "category": "Category",
    "price": "Price (USD)",
    "rating": "Rating",
    "in_stock": "In Stock",
    "id": "Product ID",
}


def collect_results() -> tuple[list[Result], list[str], Catalog, dict[str, tuple[Any, ...]]]:
    """Run the five queries and collect the catalog for the reports."""
    ## Set up the sample catalog.
    connection = create_database()
    cursor = connection.cursor()
    results: list[tuple[str, tuple[str, ...], list[tuple[Any, ...]]]] = []
    queries: list[str] = []


    def run_query(sql: str) -> list[tuple[Any, ...]]:
        """Run a query and retain its SQL for the standalone report."""
        queries.append(dedent(sql).strip())
        cursor.execute(sql)
        return cursor.fetchall()


    ## Answer the five product-finder questions.
    print("=== Out-of-Stock Products ===")
    rows = run_query("""
        SELECT name, category
        FROM products
        WHERE in_stock = 0
    """)
    results.append(("Which products are out of stock?", ("name", "category"), rows))
    for name, category in rows:
        print(f"  {name} ({category})")

    print("\n=== Rated 4.5 or Higher and Under $100 ===")
    rows = run_query("""
        SELECT name, rating, price
        FROM products
        WHERE rating >= 4.5 AND price < 100.00
    """)
    results.append((
        "Which products have a rating of 4.5 or higher AND cost less than $100?",
        ("name", "rating", "price"),
        rows,
    ))
    for name, rating, price in rows:
        print(f"  {name}: Rating {rating}, ${price:.2f}")

    print("\n=== 3 Most Expensive Accessories ===")
    rows = run_query("""
        SELECT name, price
        FROM products
        WHERE category = 'Accessories'
        ORDER BY price DESC
        LIMIT 3
    """)
    results.append((
        'What are the 3 most expensive products in the "Accessories" category?',
        ("name", "price"),
        rows,
    ))
    for name, price in rows:
        print(f"  {name}: ${price:.2f}")

    print("\n=== Products with Monitor in the Name ===")
    rows = run_query("""
        SELECT *
        FROM products
        WHERE name LIKE '%Monitor%'
    """)
    results.append((
        'Which products have "Monitor" in their name?',
        ("id", "name", "category", "price", "rating", "in_stock"),
        rows,
    ))
    for product_id, name, category, price, rating, in_stock in rows:
        print(
            f"  ID: {product_id}, Name: {name}, Category: {category}, "
            f"Price: ${price:.2f}, Rating: {rating}, In stock: {in_stock}"
        )

    print("\n=== In-Stock Products Outside Accessories ===")
    rows = run_query("""
        SELECT name, category, price
        FROM products
        WHERE category != 'Accessories' AND in_stock = 1
        ORDER BY category, price
    """)
    results.append((
        'Which products are NOT in the "Accessories" category and are in stock?',
        ("name", "category", "price"),
        rows,
    ))
    for name, category, price in rows:
        print(f"  {name} ({category}): ${price:.2f}")

    catalog = cursor.execute(
        "SELECT id, name, category, price, rating, in_stock FROM products"
    ).fetchall()
    catalog_by_name = {product[1]: product for product in catalog}
    if len(catalog_by_name) != len(catalog):
        raise ValueError("Product names must be unique when exporting catalog details.")

    connection.close()
    return results, queries, catalog, catalog_by_name


def natural_list(items: list[str]) -> str:
    """Join product names and descriptions into a readable list."""
    if not items:
        return "none"
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def build_inventory_summary(results: list[Result], catalog: Catalog) -> tuple[str, str]:
    """Summarize availability and clearly identify unrecorded inventory data."""
    in_stock_count = sum(product[5] == 1 for product in catalog)
    category_counts = {
        category: (
            sum(product[2] == category and product[5] == 1 for product in catalog),
            sum(product[2] == category for product in catalog),
        )
        for category in ("Accessories", "Displays", "Audio", "Storage")
    }
    category_details = natural_list([
        f"{available} of {total} {category}"
        for category, (available, total) in category_counts.items()
    ])
    out_of_stock = natural_list([
        f"{name} in {category}" for name, category in results[0][2]
    ])
    rated_products = natural_list([row[0] for row in results[1][2]])
    expensive_accessories = natural_list([row[0] for row in results[2][2]])
    monitors = natural_list([
        f"{name} ({'in stock' if in_stock else 'out of stock'})"
        for _, name, _, _, _, in_stock in results[3][2]
    ])
    other_products = natural_list([row[0] for row in results[4][2]])
    inventory_summary = (
        (
            f"This report covers November 2026, with November 21 requested as the report date. "
            f"The sample catalog contains {len(catalog)} products across Accessories, Displays, "
            f"Audio, and Storage. Its current stock flags mark {in_stock_count} products in "
            f"stock and {len(catalog) - in_stock_count} out of stock. These figures count "
            "products, not individual units. The sample does not record when these flags were "
            "updated, so they cannot confirm availability on November 21 or throughout the "
            f"month. The products marked out of stock are {out_of_stock}. "
            f"In-stock flags cover {category_details}. "
            f"{len(results[1][2])} products meet the high rating and price criteria: "
            f"{rated_products}. The highest priced accessories are {expensive_accessories}."
        ),
        (
            f"{len(results[3][2])} monitor products appear in the catalog: {monitors}. "
            f"{len(results[4][2])} in-stock products fall outside Accessories: {other_products}. "
            "The source does not contain opening inventory, quantities currently on hand, "
            "quantities remaining at month end, or quantities sold. Consequently, no monthly "
            "sales total, sell-through rate, remaining unit count, revenue, or movement trend "
            "can be calculated. An out-of-stock flag does not establish that an item sold "
            "during November; it could reflect an undated stock condition. Likewise, an "
            "in-stock flag does not reveal how many units remain. For a complete monthly "
            "inventory report, record each product's opening balance, dated sales, returns, "
            "receipts, and adjustments, then reconcile those movements with a dated closing "
            "balance. Until those records are supplied, all missing quantities and monthly "
            "sales figures should be treated as unavailable, not zero. The CSV identifies "
            "these gaps alongside the available catalog details, and the Word tables retain "
            "the original answers."
        ),
    )
    return inventory_summary


def format_catalog_row(product: tuple[Any, ...]) -> dict[str, Any]:
    """Format catalog values for the CSV report."""
    values: dict[str, Any] = dict(
        zip(("id", "name", "category", "price", "rating", "in_stock"), product)
    )
    formatted = {}
    for field, label in FIELD_LABELS.items():
        value = values[field]
        if field == "price":
            formatted[label] = f"{value:.2f}"
        elif field == "in_stock":
            formatted[label] = "Yes" if value else "No"
        else:
            formatted[label] = value
    return formatted


def write_csv(csv_path: Path, results: list[Result], catalog_by_name: dict[str, tuple[Any, ...]]) -> None:
    """Export a filterable CSV of all query results."""
    result_groups = (
        "Out of stock",
        "Rating >= 4.5 and price < $100",
        "3 most expensive accessories",
        "Monitors",
        "In stock, not accessories",
    )

    ## Keep one rectangular table so the CSV can be filtered in a spreadsheet.
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        fieldnames = [
            "Question Number", "Result Group", *FIELD_LABELS.values(),
            "Reporting Month", "Stock Snapshot Date",
            "Current Units", "Month-End Units", "Units Sold in Month",
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for number, (_, columns, rows) in enumerate(results, 1):
            for row in rows:
                query_values = dict(zip(columns, row))
                formatted = format_catalog_row(catalog_by_name[query_values["name"]])
                writer.writerow({
                    "Question Number": number,
                    "Result Group": result_groups[number - 1],
                    **formatted,
                    "Reporting Month": "November 2026",
                    "Stock Snapshot Date": NOT_RECORDED,
                    "Current Units": NOT_RECORDED,
                    "Month-End Units": NOT_RECORDED,
                    "Units Sold in Month": NOT_RECORDED,
                })


def write_sql(sql_path: Path, results: list[Result], queries: list[str]) -> None:
    """Export the queries for an existing SQLite catalog."""
    ## Export queries and results for an existing SQLite products table.
    with sql_path.open("w", encoding="utf-8", newline="\n") as sql_file:
        sql_file.write("-- Run these queries against an existing SQLite products table.\n")
        for number, ((question, columns, rows), query) in enumerate(zip(results, queries), 1):
            sql_file.write(f"\n-- {number}. {question}\n")
            sql_file.write(query + ";\n")
            sql_file.write("-- Results: " + " | ".join(columns) + "\n")
            if not rows:
                sql_file.write("-- No matching products.\n")
            for row in rows:
                sql_file.write("-- " + " | ".join(str(value) for value in row) + "\n")


def add_result_tables(document: Any, results: list[Result]) -> None:
    """Add the five labeled result tables to the Word report."""
    for number, (question, columns, rows) in enumerate(results, 1):
        document.add_heading(f"{number}. {question}", level=1)
        if not rows:
            document.add_paragraph("No matching products.")
            continue
        table = document.add_table(rows=1, cols=len(columns))
        table.style = "Light Shading Accent 1"
        for cell, column in zip(table.rows[0].cells, columns):
            cell.text = column.replace("_", " ").title()
            cell.paragraphs[0].runs[0].bold = True
        for row in rows:
            cells = table.add_row().cells
            for cell, column, value in zip(cells, columns, row):
                cell.text = f"${value:.2f}" if column == "price" else str(value)


def add_findings_summary(document: Any, results: list[Result]) -> None:
    """Add a concise summary of the five query results."""
    document.add_heading("Summary of Findings", level=1)
    paragraph = document.add_paragraph()
    paragraph.add_run("Out of stock: ").bold = True
    paragraph.add_run(
        "; ".join(f"{name} ({category})" for name, category in results[0][2])
        or NO_PRODUCTS
    )
    paragraph.add_run(". ")
    paragraph.add_run("Rated at least 4.5 and under $100: ").bold = True
    paragraph.add_run(
        "; ".join(
            f"{name} (rating {rating}, ${price:.2f})"
            for name, rating, price in results[1][2]
        ) or NO_PRODUCTS
    )
    paragraph.add_run(". ")
    paragraph.add_run("Three most expensive accessories: ").bold = True
    paragraph.add_run(
        "; ".join(f"{name} (${price:.2f})" for name, price in results[2][2])
        or NO_PRODUCTS
    )
    paragraph.add_run(".")

    paragraph = document.add_paragraph()
    paragraph.add_run("Monitors: ").bold = True
    paragraph.add_run(
        "; ".join(
            f"{name} (ID {product_id}, {category}, ${price:.2f}, "
            f"rating {rating}, {'in stock' if in_stock else 'out of stock'})"
            for product_id, name, category, price, rating, in_stock in results[3][2]
        ) or NO_PRODUCTS
    )
    paragraph.add_run(". ")
    paragraph.add_run("In-stock products outside Accessories: ").bold = True
    paragraph.add_run(
        "; ".join(
            f"{name} ({category}, ${price:.2f})"
            for name, category, price in results[4][2]
        ) or NO_PRODUCTS
    )
    paragraph.add_run(".")


def write_docx(docx_path: Path, results: list[Result], inventory_summary: tuple[str, str]) -> None:
    """Write the formatted Word report."""
    if Document is None:
        raise SystemExit("Word export requires python-docx. Run: pip install -r requirements.txt")
    document = Document()
    document.styles["Title"].font.bold = True
    document.add_heading("Product Finder Results", level=0)
    add_result_tables(document, results)
    add_findings_summary(document, results)
    document.add_heading("Monthly Inventory Summary", level=1)
    for summary_paragraph in inventory_summary:
        document.add_paragraph(summary_paragraph)
    document.save(docx_path)


def open_reports(csv_path: Path, docx_path: Path) -> None:
    """Request both Windows report viewers and report any launch errors."""
    open_errors = []
    for report_path in (csv_path, docx_path):
        try:
            os.startfile(report_path)
        except OSError as error:
            open_errors.append(f"Could not open {report_path}: {error}")
        else:
            print(f"Requested Windows to open {report_path.name}; this may take a few seconds.")

    if open_errors:
        raise SystemExit("\n".join(open_errors))


def main() -> None:
    """Run the queries, export the reports, and open the results."""
    results, queries, catalog, catalog_by_name = collect_results()
    inventory_summary = build_inventory_summary(results, catalog)
    output_directory = Path(__file__).resolve().parent
    csv_path = output_directory / "product_finder_results.csv"
    docx_path = output_directory / "product_finder_results.docx"
    sql_path = output_directory / "product_finder_results.sql"
    write_csv(csv_path, results, catalog_by_name)
    write_sql(sql_path, results, queries)
    write_docx(docx_path, results, inventory_summary)
    print(f"\nCSV results saved to: {csv_path}")
    print(f"Word results saved to: {docx_path}")
    print(f"SQL results saved to: {sql_path}")
    open_reports(csv_path, docx_path)


if __name__ == "__main__":
    main()
