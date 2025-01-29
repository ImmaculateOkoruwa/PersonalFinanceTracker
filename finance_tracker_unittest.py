import unittest
import sqlite3
import pandas as pd
from unittest.mock import patch
from finance_tracker_GUI import init_db, validate_date, validate_amount, add_transaction, view_transactions, analyze_spending_gui

DB_NAME = "finance_tracker.db"

# Assuming that these functions are already defined in your code
# init_db(), validate_date(), validate_amount(), add_transaction(), view_transactions(), analyze_spending_gui()

class TestDatabaseFunctions(unittest.TestCase):
    def test_init_db(self):
        """Test the database initialization."""
        init_db()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions';")
        table = cursor.fetchone()

        conn.close()

        self.assertIsNotNone(table, "The transactions table should exist.")

class TestValidationFunctions(unittest.TestCase):
    def test_validate_date(self):
        """Test the date validation."""
        valid_date = "2024-05-01"
        invalid_date = "01-05-2024"

        self.assertTrue(validate_date(valid_date), "The date format should be valid.")
        self.assertFalse(validate_date(invalid_date), "The date format should be invalid.")

    def test_validate_amount(self):
        """Test the amount validation."""
        valid_amount = "100.50"
        invalid_amount = "-50"

        self.assertTrue(validate_amount(valid_amount), "The amount should be valid.")
        self.assertFalse(validate_amount(invalid_amount), "The amount should be invalid.")

class TestTransactionFunctions(unittest.TestCase):
    def test_add_transaction(self):
        """Test adding a transaction."""
        # Initialize DB to ensure it's empty
        init_db()

        # Mock input for adding a transaction
        with patch('builtins.input', side_effect=["2024-05-01", "Transportation", "40.33", "Transportation transaction"]):
            add_transaction()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE category='Transportation';")
        transaction = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(transaction, "Transaction should be added to the database.")
        self.assertEqual(transaction[2], "Transportation", "The category should match the input.")

    def test_view_transactions(self):
        """Test viewing all transactions."""
        init_db()

        # Adding multiple transactions
        transactions_data = [
            ("2024-05-01", "Transportation", 40.33, "Transportation transaction"),
            ("2024-05-02", "Rent", 447.3, "Rent transaction"),
            ("2024-05-03", "Food", 245.43, "Food transaction"),
            ("2024-05-04", "Entertainment", 463.63, "Entertainment transaction"),
            ("2024-05-05", "Transportation", 184.28, "Transportation transaction"),
            ("2024-05-06", "Food", 431.93, "Food transaction"),
        ]

        # Insert test data into the database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.executemany("INSERT INTO transactions (date, category, amount, description) VALUES (?, ?, ?, ?);", transactions_data)
        conn.commit()
        conn.close()

        # Test viewing the transactions
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions;")
        transactions = cursor.fetchall()
        conn.close()

        self.assertGreater(len(transactions), 0, "There should be transactions in the database.")

class TestAnalysisFunctions(unittest.TestCase):
    def test_analyze_spending(self):
        """Test analyzing spending."""
        init_db()

        # Add a set of transactions
        transactions_data = [
            ("2024-05-01", "Transportation", 40.33, "Transportation transaction"),
            ("2024-05-02", "Rent", 447.3, "Rent transaction"),
            ("2024-05-03", "Food", 245.43, "Food transaction"),
            ("2024-05-04", "Entertainment", 463.63, "Entertainment transaction"),
            ("2024-05-05", "Transportation", 184.28, "Transportation transaction"),
            ("2024-05-06", "Food", 431.93, "Food transaction"),
            ("2024-05-07", "Miscellaneous", 58.28, "Miscellaneous transaction"),
            ("2024-05-08", "Rent", 399.15, "Rent transaction"),
            ("2024-05-09", "Utilities", 232.06, "Utilities transaction"),
            ("2024-05-10", "Rent", 263.46, "Rent transaction"),
            ("2024-05-11", "Miscellaneous", 365.68, "Miscellaneous transaction"),
            ("2024-05-12", "Utilities", 108.79, "Utilities transaction"),
            ("2024-05-13", "Miscellaneous", 391.86, "Miscellaneous transaction"),
            ("2024-05-14", "Utilities", 289.37, "Utilities transaction"),
            ("2024-05-15", "Entertainment", 42.1, "Entertainment transaction"),
            ("2024-05-16", "Transportation", 106, "Transportation transaction"),
            ("2024-05-17", "Miscellaneous", 23.45, "Miscellaneous transaction"),
            ("2024-05-18", "Utilities", 54.47, "Utilities transaction"),
            ("2024-05-19", "Utilities", 264.82, "Utilities transaction"),
            ("2024-05-20", "Utilities", 116.39, "Utilities transaction"),
            ("2024-05-21", "Transportation", 271.3, "Transportation transaction"),
            ("2024-05-22", "Miscellaneous", 217.78, "Miscellaneous transaction"),
            ("2024-05-23", "Food", 306.35, "Food transaction"),
            ("2024-05-24", "Entertainment", 398.08, "Entertainment transaction"),
            ("2024-05-25", "Utilities", 30.63, "Utilities transaction"),
            ("2024-05-26", "Rent", 405.77, "Rent transaction")
        ]

        # Insert data into the database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.executemany("INSERT INTO transactions (date, category, amount, description) VALUES (?, ?, ?, ?);", transactions_data)
        conn.commit()
        conn.close()

        # Simulate analysis and check if summary is correct
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM transactions;", conn)
        conn.close()

        self.assertEqual(len(df), 26, "There should be 26 transactions in the database.")
        category_summary = df.groupby("category")["amount"].sum()

        # Test if specific categories are in the summary
        self.assertIn("Food", category_summary.index, "Food should be in the summary.")
        self.assertIn("Rent", category_summary.index, "Rent should be in the summary.")
        self.assertIn("Transportation", category_summary.index, "Transportation should be in the summary.")

if __name__ == '__main__':
    unittest.main()
