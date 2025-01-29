from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_NAME = "finance_tracker.db"


def db_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access
    return conn


@app.route('/', methods=['GET'])
def home():
    """Root endpoint with API documentation."""
    return jsonify({
        "message": "Welcome to the Finance Tracker API. Here are the available endpoints:",
        "endpoints": {
            "/transactions": "GET all transactions",
            "/transactions/date_range": "GET transactions within a specific date range (requires start_date and end_date as query params)",
            "/transactions/category": "GET transactions by category (requires category as a query param)",
            "/transactions/above_amount": "GET transactions above a certain amount (requires min_amount as a query param)",
            "/transactions/monthly_summary": "GET monthly spending summary",
            "/transactions/keyword": "GET transactions with a specific keyword in the description (requires keyword as a query param)"
        }
    }), 200


@app.route('/transactions', methods=['GET'])
def get_all_transactions():
    """Retrieve all transactions."""
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions;")
    transactions = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in transactions])


# Example query for /transactions:
# GET http://127.0.0.1:5000/transactions

@app.route('/transactions/date_range', methods=['GET'])
def get_transactions_by_date_range():
    """Retrieve transactions within a specific date range."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Example query for /transactions/date_range:
    # GET http://127.0.0.1:5000/transactions/date_range?start_date=2024-01-01&end_date=2024-12-31

    if not start_date or not end_date:
        return jsonify({"error": "Both 'start_date' and 'end_date' are required"}), 400

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE date BETWEEN ? AND ?;", (start_date, end_date))
    transactions = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in transactions])


@app.route('/transactions/category', methods=['GET'])
def get_transactions_by_category():
    """Retrieve transactions by category."""
    category = request.args.get('category')

    # Example query for /transactions/category:
    # GET http://127.0.0.1:5000/transactions/category?category=Food

    if not category:
        return jsonify({"error": "'category' parameter is required"}), 400

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE category = ?;", (category,))
    transactions = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in transactions])


@app.route('/transactions/above_amount', methods=['GET'])
def get_transactions_above_amount():
    """Retrieve transactions with amounts greater than a specified value."""
    min_amount = request.args.get('min_amount', type=float)

    # Example query for /transactions/above_amount:
    # GET http://127.0.0.1:5000/transactions/above_amount?min_amount=100

    if not min_amount:
        return jsonify({"error": "'min_amount' parameter is required"}), 400

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE amount > ?;", (min_amount,))
    transactions = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in transactions])


@app.route('/transactions/monthly_summary', methods=['GET'])
def get_monthly_spending_summary():
    """Retrieve monthly spending summary."""
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT strftime('%Y-%m', date) AS month, SUM(amount) AS total_spent
        FROM transactions
        GROUP BY month;
    """)
    summary = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in summary])


# Example query for /transactions/monthly_summary:
# GET http://127.0.0.1:5000/transactions/monthly_summary

@app.route('/transactions/keyword', methods=['GET'])
def get_transactions_by_keyword():
    """Retrieve transactions by a keyword in the description."""
    keyword = request.args.get('keyword')

    # Example query for /transactions/keyword:
    # GET http://127.0.0.1:5000/transactions/keyword?keyword=groceries

    if not keyword:
        return jsonify({"error": "'keyword' parameter is required"}), 400

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE description LIKE ?;", (f"%{keyword}%",))
    transactions = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in transactions])


if __name__ == "__main__":
    app.run(debug=True)
