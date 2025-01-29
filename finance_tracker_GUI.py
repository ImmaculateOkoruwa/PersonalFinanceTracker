import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import re

DB_NAME = "finance_tracker.db"


def init_db():
    """Initialize the database with the correct table schema."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Drop the table if it already exists to avoid column mismatch errors
        cursor.execute("DROP TABLE IF EXISTS transactions")

        # Create the table with the correct columns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT
            );
        """)
        conn.commit()
        conn.close()
        print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")


def validate_date(date):
    """Validate date format (YYYY-MM-DD)."""
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    return re.match(pattern, date)


def validate_amount(amount):
    """Validate positive numeric input."""
    try:
        return float(amount) > 0
    except ValueError:
        return False


def upload_csv():
    """Upload a CSV file and insert the data into the database."""
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        try:
            # Read the CSV into a pandas DataFrame
            df = pd.read_csv(file_path)

            # Check if the necessary columns are present
            required_columns = ['date', 'category', 'amount', 'description']
            if not all(col in df.columns for col in required_columns):
                messagebox.showerror("Invalid CSV", "CSV must contain columns: date, category, amount, description.")
                return

            # Insert data into the database
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO transactions (date, category, amount, description)
                    VALUES (?, ?, ?, ?);
                """, (row['date'], row['category'], row['amount'], row['description']))
            conn.commit()
            conn.close()
            messagebox.showinfo("CSV Upload", "CSV file uploaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload CSV: {e}")


def menu():
    """Display menu options."""
    print("\n=== Personal Finance Tracker ===")
    print("[1] Add Transaction")
    print("[2] View Transactions")
    print("[3] Analyze Spending")
    print("[4] Upload CSV")
    print("[5] Exit")


def add_transaction():
    """Add a new transaction to the database."""
    date = input("Enter transaction date (YYYY-MM-DD): ")
    if not validate_date(date):
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    category = input("Enter transaction category (e.g., Food, Rent): ")
    amount = input("Enter transaction amount: ")
    if not validate_amount(amount):
        print("Invalid amount. Please enter a positive number.")
        return

    description = input("Enter transaction description (optional): ")

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (date, category, amount, description)
            VALUES (?, ?, ?, ?);
        """, (date, category, float(amount), description))
        conn.commit()
        conn.close()
        print("Transaction added successfully!")
    except sqlite3.Error as e:
        print(f"Error adding transaction: {e}")


def view_transactions():
    """View all transactions in the database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions;")
        transactions = cursor.fetchall()
        conn.close()

        if not transactions:
            messagebox.showinfo("No Data", "No transactions found.")
            return

        # Clear previous transaction display
        for widget in transaction_display.winfo_children():
            widget.destroy()

        # Create a canvas for scrollable area
        canvas = tk.Canvas(transaction_display)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a scrollbar
        scrollbar = tk.Scrollbar(transaction_display, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame for transactions inside the canvas
        transaction_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=transaction_frame, anchor="nw")

        # Display each transaction
        for txn in transactions:
            transaction_label = tk.Label(transaction_frame, text=f"ID: {txn[0]}, Date: {txn[1]}, "
                                                                 f"Category: {txn[2]}, Amount: ${txn[3]:.2f}, "
                                                                 f"Description: {txn[4]}")
            transaction_label.pack(anchor="w", pady=2)

        # Update the scroll region of the canvas
        transaction_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Error retrieving transactions: {e}")


def analyze_spending_gui():
    """Analyze spending using Pandas and Matplotlib and display results on the GUI."""
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM transactions;", conn)
        conn.close()

        if df.empty:
            messagebox.showinfo("No Data", "No transactions to analyze.")
            return

        # Convert date to datetime and extract month and year
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')

        # Monthly spending summary
        monthly_summary = df.groupby("month")["amount"].sum()

        # Clear previous analysis output
        for widget in analysis_frame.winfo_children():
            widget.destroy()

        # Display analysis summary
        analysis_label = tk.Label(analysis_frame, text="Spending by Category:")
        analysis_label.pack(anchor="w")

        # Category spending summary
        category_summary = df.groupby("category")["amount"].sum()
        for category, amount in category_summary.items():
            summary_label = tk.Label(analysis_frame, text=f"{category}: ${amount:.2f}")
            summary_label.pack(anchor="w", pady=2)

        # Create pie chart for spending by category
        fig1, ax1 = plt.subplots(1, 2, figsize=(10, 5))

        # Pie chart
        category_summary.plot(kind="pie", autopct="%1.1f%%", startangle=140, ax=ax1[0])
        ax1[0].set_title("Spending by Category")
        ax1[0].set_ylabel("")  # Hide y-axis label

        # Bar chart for monthly spending
        monthly_summary.plot(kind="bar", ax=ax1[1])
        ax1[1].set_title("Monthly Spending")
        ax1[1].set_ylabel("Amount ($)")

        plt.tight_layout()

        # Embed the chart into the Tkinter window
        canvas = FigureCanvasTkAgg(fig1, master=analysis_frame)  # Create a canvas for Tkinter
        canvas.draw()  # Render the plot
        canvas.get_tk_widget().pack()  # Add the widget to the window

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Error analyzing spending: {e}")


def main_gui():
    """Create the GUI and run the finance tracker."""
    # Initialize database
    init_db()

    # Create main window
    root = tk.Tk()
    root.title("Personal Finance Tracker")
    root.geometry("600x400")

    # Transaction Frame
    transaction_frame = tk.Frame(root)
    transaction_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    # Add transaction button
    add_btn = tk.Button(transaction_frame, text="Add Transaction", command=add_transaction)
    add_btn.pack(pady=5)

    # View transactions button
    view_btn = tk.Button(transaction_frame, text="View Transactions", command=view_transactions)
    view_btn.pack(pady=5)

    # Analyze spending button
    analyze_btn = tk.Button(transaction_frame, text="Analyze Spending", command=analyze_spending_gui)
    analyze_btn.pack(pady=5)

    # Upload CSV button
    upload_btn = tk.Button(transaction_frame, text="Upload CSV", command=upload_csv)
    upload_btn.pack(pady=5)

    # Transaction display frame (updated on view)
    global transaction_display
    transaction_display = tk.Frame(root)
    transaction_display.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    # Spending Analysis Frame
    global analysis_frame
    analysis_frame = tk.Frame(root)
    analysis_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    # Start GUI loop
    root.mainloop()


if __name__ == "__main__":
    main_gui()
