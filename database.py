import sqlite3
import os


# Database location
DATABASE_FOLDER = "data"
DATABASE_FILE = os.path.join(DATABASE_FOLDER, "expense_tracker.db")


def create_database():
    """
    Creates the database folder and transactions table.
    """

    # Create data folder if it doesn't exist
    if not os.path.exists(DATABASE_FOLDER):
        os.makedirs(DATABASE_FOLDER)

    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT
        )
    """)
   # ========================================================
    # BUDGET TABLE
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY,
            amount REAL NOT NULL
        )
    """)
    
    connection.commit()
    connection.close()


def add_transaction(
    transaction_type,
    amount,
    category,
    payment_method,
    date,
    description
):
    """
    Adds a new transaction to the database.
    """

    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO transactions
        (
            transaction_type,
            amount,
            category,
            payment_method,
            date,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        transaction_type,
        amount,
        category,
        payment_method,
        date,
        description
    ))

    connection.commit()
    connection.close()


def get_transactions():
    """
    Returns all transactions.
    """

    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            transaction_type,
            amount,
            category,
            payment_method,
            date,
            description
        FROM transactions
        ORDER BY date DESC, id DESC
    """)

    transactions = cursor.fetchall()

    connection.close()

    return transactions


def get_total_income():
    """
    Calculates total income.
    """

    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE transaction_type = 'Income'
    """)

    total = cursor.fetchone()[0]

    connection.close()

    return total


def get_total_expenses():
    """
    Calculates total expenses.
    """

    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE transaction_type = 'Expense'
    """)

    total = cursor.fetchone()[0]

    connection.close()

    return total

def delete_transaction(transaction_id):
    """
    Deletes a transaction using its ID.
    """

    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM transactions
        WHERE id = ?
    """, (transaction_id,))

    connection.commit()
    connection.close()


def update_transaction(
    transaction_id,
    transaction_type,
    amount,
    category,
    payment_method,
    date,
    description
):
    """
    Updates an existing transaction.
    """

    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE transactions
        SET
            transaction_type = ?,
            amount = ?,
            category = ?,
            payment_method = ?,
            date = ?,
            description = ?
        WHERE id = ?
    """, (
        transaction_type,
        amount,
        category,
        payment_method,
        date,
        description,
        transaction_id
    ))

    connection.commit()
    connection.close()
    
def search_transactions(search_text="", transaction_type="All", category="All"):
    """
    Searches and filters transactions.
    """

    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    query = """
        SELECT
            id,
            transaction_type,
            amount,
            category,
            payment_method,
            date,
            description
        FROM transactions
        WHERE 1=1
    """

    parameters = []

    # Filter by transaction type
    if transaction_type != "All":

        query += """
            AND transaction_type = ?
        """

        parameters.append(transaction_type)


    # Filter by category
    if category != "All":

        query += """
            AND category = ?
        """

        parameters.append(category)


    # Search
    if search_text:

        query += """
            AND (
                category LIKE ?
                OR description LIKE ?
                OR payment_method LIKE ?
            )
        """

        search_value = f"%{search_text}%"

        parameters.append(search_value)
        parameters.append(search_value)
        parameters.append(search_value)


    query += """
        ORDER BY date DESC, id DESC
    """


    cursor.execute(
        query,
        parameters
    )

    transactions = cursor.fetchall()

    connection.close()

    return transactions

# ========================================================
# BUDGET FUNCTIONS
# ========================================================

def get_budget():
    """
    Get the current monthly budget.
    Returns 0 if no budget has been set.
    """

    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute(
        "SELECT amount FROM budget WHERE id = 1"
    )

    result = cursor.fetchone()

    connection.close()

    if result:
        return result[0]

    return 0


def save_budget(amount):
    """
    Save or update the monthly budget.
    """

    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO budget (id, amount)
        VALUES (1, ?)
    """, (amount,))

    connection.commit()

    connection.close()
    
def get_monthly_expenses(month, year):
    """
    Returns total expenses for a particular month and year.
    """

    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE transaction_type = 'Expense'
        AND strftime('%m', date) = ?
        AND strftime('%Y', date) = ?
    """, (
        f"{month:02d}",
        str(year)
    ))

    total = cursor.fetchone()[0]

    connection.close()

    return total


def get_monthly_income(month, year):
    """
    Returns total income for a particular month and year.
    """

    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE transaction_type = 'Income'
        AND strftime('%m', date) = ?
        AND strftime('%Y', date) = ?
    """, (
        f"{month:02d}",
        str(year)
    ))

    total = cursor.fetchone()[0]

    connection.close()

    return total


def get_monthly_transactions(month, year):
    """
    Returns transactions for a particular month and year.
    """

    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            transaction_type,
            amount,
            category,
            payment_method,
            date,
            description
        FROM transactions
        WHERE strftime('%m', date) = ?
        AND strftime('%Y', date) = ?
        ORDER BY date DESC, id DESC
    """, (
        f"{month:02d}",
        str(year)
    ))

    transactions = cursor.fetchall()

    connection.close()

    return transactions