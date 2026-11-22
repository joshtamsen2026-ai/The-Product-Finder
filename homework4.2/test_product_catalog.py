"""Focused tests for the shared catalog and import-safe exercises."""

import contextlib
import importlib.util
import io
import runpy
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from product_catalog import create_database


class ProductCatalogTests(unittest.TestCase):
    def test_databases_are_independent(self) -> None:
        """Changing one temporary catalog must not affect another."""
        first = create_database()
        second = create_database()
        self.addCleanup(first.close)
        self.addCleanup(second.close)

        first.execute("UPDATE products SET in_stock = 0 WHERE name = ?", ("Wireless Mouse",))
        stock = second.execute(
            "SELECT in_stock FROM products WHERE name = ?", ("Wireless Mouse",)
        ).fetchone()
        self.assertEqual(stock, (1,))

    def test_exercise_imports_do_not_run_the_programs(self) -> None:
        """Importing either script must not create reports or launch applications."""
        root = Path(__file__).resolve().parent
        for name in ("product_finder", "product_queries"):
            with self.subTest(script=name):
                spec = importlib.util.spec_from_file_location(name, root / f"{name}.py")
                self.assertIsNotNone(spec)
                self.assertIsNotNone(spec.loader)
                module = importlib.util.module_from_spec(spec)
                with patch("product_catalog.create_database") as create, contextlib.redirect_stdout(
                    io.StringIO()
                ) as output:
                    spec.loader.exec_module(module)
                create.assert_not_called()
                self.assertEqual(output.getvalue(), "")

    def test_sql_export_queries_existing_catalog(self) -> None:
        """The generated SQL must query an existing catalog without modifying it."""
        root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as temporary:
            script = Path(temporary) / "product_finder.py"
            shutil.copyfile(root / script.name, script)
            with patch("os.startfile", create=True), contextlib.redirect_stdout(io.StringIO()):
                runpy.run_path(str(script), run_name="__main__")

            sql = (Path(temporary) / "product_finder_results.sql").read_text(encoding="utf-8")
            connection = create_database()
            self.addCleanup(connection.close)
            results = []
            statement = ""
            for line in sql.splitlines(keepends=True):
                statement += line
                if sqlite3.complete_statement(statement):
                    cursor = connection.execute(statement)
                    if cursor.description:
                        results.append(cursor.fetchall())
                    statement = ""

            self.assertEqual([len(rows) for rows in results], [2, 3, 3, 2, 6])
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM products").fetchone(), (12,))


if __name__ == "__main__":
    unittest.main()
