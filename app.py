import calendar
from datetime import date

import matplotlib.pyplot as plt
import streamlit as st

from database import (
    create_database,
    add_transaction,
    get_budget,
    save_budget,
    get_transactions,
    get_total_income,
    get_total_expenses,
    delete_transaction,
    update_transaction,
    search_transactions,
    get_monthly_expenses,
    get_monthly_income,
    get_monthly_transactions,
)

# ------------------------------------------------------------
# Page setup and database initialization
# ------------------------------------------------------------
st.set_page_config(
    page_title="SpendWise | Personal Expense Tracker",
    page_icon="💰",
    layout="wide",
)

create_database()

CATEGORIES = [
    "Food", "Transport", "Shopping", "Education", "Entertainment",
    "Bills", "Health", "Travel", "Other",
]
PAYMENT_METHODS = [
    "UPI", "Cash", "Credit Card", "Debit Card", "Bank Transfer", "Other",
]
TRANSACTION_TYPES = ["Expense", "Income"]


def money(value):
    return f"₹{float(value or 0):,.2f}"


def show_transaction_form(prefix, transaction=None):
    """Render a reusable add/edit transaction form."""
    editing = transaction is not None
    with st.form(f"{prefix}_transaction_form"):
        left, right = st.columns(2)
        default_type = transaction[1] if editing else "Expense"
        default_amount = float(transaction[2]) if editing else 0.0
        default_category = transaction[3] if editing and transaction[3] in CATEGORIES else "Food"
        default_payment = transaction[4] if editing and transaction[4] in PAYMENT_METHODS else "UPI"
        try:
            default_date = date.fromisoformat(str(transaction[5])) if editing else date.today()
        except (TypeError, ValueError):
            default_date = date.today()
        default_description = str(transaction[6] or "") if editing else ""

        with left:
            tx_type = st.selectbox(
                "Transaction type", TRANSACTION_TYPES,
                index=TRANSACTION_TYPES.index(default_type),
                key=f"{prefix}_type",
            )
            amount = st.number_input(
                "Amount (₹)", min_value=0.01, value=max(default_amount, 0.01),
                step=50.0, format="%.2f", key=f"{prefix}_amount",
            )
            category = st.selectbox(
                "Category", CATEGORIES, index=CATEGORIES.index(default_category),
                key=f"{prefix}_category",
            )
        with right:
            payment = st.selectbox(
                "Payment method", PAYMENT_METHODS,
                index=PAYMENT_METHODS.index(default_payment),
                key=f"{prefix}_payment",
            )
            tx_date = st.date_input("Date", value=default_date, key=f"{prefix}_date")
            description = st.text_input(
                "Description (optional)", value=default_description,
                max_chars=250, key=f"{prefix}_description",
            )

        submitted = st.form_submit_button(
            "Save changes" if editing else "Add transaction",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if amount <= 0:
            st.error("Amount must be greater than zero.")
            return False
        values = (
            tx_type, float(amount), category, payment,
            tx_date.isoformat(), description.strip(),
        )
        if editing:
            update_transaction(transaction[0], *values)
            st.success("Transaction updated.")
        else:
            add_transaction(*values)
            st.success("Transaction added.")
        st.rerun()
    return False


# ------------------------------------------------------------
# Sidebar navigation
# ------------------------------------------------------------
st.sidebar.title("💰 SpendWise")
st.sidebar.caption("Personal Expense Tracker")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add transaction", "All transactions", "Monthly budget", "Analytics"],
)
st.sidebar.divider()
st.sidebar.caption("Track your income, expenses, and monthly budget.")

# ------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------
if page == "Dashboard":
    st.title("Welcome to SpendWise")
    st.write("A simple overview of your personal finances.")

    income = get_total_income()
    expenses = get_total_expenses()
    balance = income - expenses

    c1, c2, c3 = st.columns(3)
    c1.metric("Total income", money(income))
    c2.metric("Total expenses", money(expenses))
    c3.metric("Available balance", money(balance))

    budget = get_budget()
    today = date.today()
    month_expenses = get_monthly_expenses(today.month, today.year)
    if budget > 0:
        st.subheader("Monthly budget")
        b1, b2 = st.columns(2)
        b1.metric("Budget", money(budget))
        b2.metric("Spent this month", money(month_expenses), delta=money(budget - month_expenses))
        st.progress(min(month_expenses / budget, 1.0))
        percentage = month_expenses / budget * 100
        st.caption(f"{percentage:.1f}% of your monthly budget used.")
        if percentage >= 100:
            st.warning("You have reached or exceeded your monthly budget.")
        elif percentage >= 80:
            st.warning("You have used at least 80% of your monthly budget.")
    else:
        st.info("No monthly budget set yet. Open **Monthly budget** to set one.")

    st.subheader("Recent transactions")
    transactions = get_transactions()[:8]
    if transactions:
        st.dataframe(
            [
                {
                    "ID": row[0], "Date": row[5], "Type": row[1],
                    "Category": row[3], "Payment": row[4],
                    "Amount": money(row[2]), "Description": row[6] or "",
                }
                for row in transactions
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No transactions yet. Add your first transaction to get started.")

# ------------------------------------------------------------
# Add transaction
# ------------------------------------------------------------
elif page == "Add transaction":
    st.title("➕ Add transaction")
    st.write("Record income or an expense.")
    show_transaction_form("add")

# ------------------------------------------------------------
# All transactions: search, filter, edit, delete
# ------------------------------------------------------------
elif page == "All transactions":
    st.title("📋 All transactions")
    with st.form("transaction_filters"):
        search_text = st.text_input("Search", placeholder="Category, description, or payment method")
        f1, f2 = st.columns(2)
        tx_filter = f1.selectbox("Transaction type", ["All"] + TRANSACTION_TYPES)
        category_filter = f2.selectbox("Category", ["All"] + CATEGORIES)
        filter_submit = st.form_submit_button("Apply filters")

    # Streamlit reruns on submit; the current widget values are used directly.
    rows = search_transactions(search_text, tx_filter, category_filter)
    if rows:
        st.dataframe(
            [
                {
                    "ID": row[0], "Date": row[5], "Type": row[1],
                    "Category": row[3], "Payment": row[4],
                    "Amount": money(row[2]), "Description": row[6] or "",
                }
                for row in rows
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Edit or delete a transaction")
        row_by_id = {str(row[0]): row for row in rows}
        chosen_id = st.selectbox(
            "Choose transaction ID",
            list(row_by_id.keys()),
            format_func=lambda value: (
                f"#{value} · {row_by_id[value][5]} · "
                f"{row_by_id[value][1]} · {row_by_id[value][3]} · "
                f"{money(row_by_id[value][2])}"
            ),
        )
        selected = row_by_id[chosen_id]
        with st.expander("Edit selected transaction"):
            show_transaction_form(f"edit_{chosen_id}", selected)
        if st.button("🗑️ Delete selected transaction", type="secondary"):
            st.session_state["confirm_delete_id"] = int(chosen_id)

        if st.session_state.get("confirm_delete_id") == int(chosen_id):
            st.warning(f"Delete transaction #{chosen_id}? This cannot be undone.")
            yes, no = st.columns(2)
            if yes.button("Yes, delete it", type="primary", key=f"confirm_delete_{chosen_id}"):
                delete_transaction(int(chosen_id))
                st.session_state.pop("confirm_delete_id", None)
                st.success("Transaction deleted.")
                st.rerun()
            if no.button("Cancel", key=f"cancel_delete_{chosen_id}"):
                st.session_state.pop("confirm_delete_id", None)
                st.rerun()
    else:
        st.info("No transactions match these filters.")

# ------------------------------------------------------------
# Monthly budget
# ------------------------------------------------------------
elif page == "Monthly budget":
    st.title("🎯 Monthly budget")
    current_budget = float(get_budget() or 0)
    with st.form("budget_form"):
        budget_amount = st.number_input(
            "Monthly spending limit (₹)", min_value=0.0,
            value=current_budget, step=500.0, format="%.2f",
        )
        save = st.form_submit_button("Save budget", type="primary")
    if save:
        save_budget(float(budget_amount))
        st.success("Monthly budget saved.")
        st.rerun()

    today = date.today()
    spent = get_monthly_expenses(today.month, today.year)
    remaining = current_budget - spent
    a, b, c = st.columns(3)
    a.metric("Budget", money(current_budget))
    b.metric("Spent this month", money(spent))
    c.metric("Remaining", money(remaining))
    if current_budget > 0:
        percentage = spent / current_budget * 100
        st.progress(min(spent / current_budget, 1.0))
        st.caption(f"{percentage:.1f}% of your budget used.")
        if percentage >= 100:
            st.error("You have exceeded your monthly budget.")
        elif percentage >= 80:
            st.warning("You have used at least 80% of your monthly budget.")
        elif percentage >= 50:
            st.info("You have used more than half of your monthly budget.")
        else:
            st.success("You are comfortably within your monthly budget.")

# ------------------------------------------------------------
# Analytics
# ------------------------------------------------------------
elif page == "Analytics":
    st.title("📊 Financial analytics")
    today = date.today()
    months = list(range(1, 13))
    years = list(range(today.year - 5, today.year + 1))
    f1, f2 = st.columns(2)
    month = f1.selectbox(
        "Month", months, index=today.month - 1,
        format_func=lambda value: calendar.month_name[value],
    )
    year = f2.selectbox("Year", years, index=len(years) - 1)

    transactions = get_monthly_transactions(month, year)
    income = get_monthly_income(month, year)
    expenses = get_monthly_expenses(month, year)
    balance = income - expenses
    savings_rate = (balance / income * 100) if income > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Income", money(income))
    c2.metric("Expenses", money(expenses))
    c3.metric("Balance", money(balance))
    c4.metric("Savings rate", f"{savings_rate:.1f}%")

    category_totals = {}
    for row in transactions:
        if row[1] == "Expense":
            category_totals[row[3]] = category_totals.get(row[3], 0) + float(row[2])

    chart_left, chart_right = st.columns(2)
    with chart_left:
        st.subheader("Expenses by category")
        if category_totals:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.pie(
                list(category_totals.values()),
                labels=list(category_totals.keys()),
                autopct="%1.1f%%",
                startangle=90,
            )
            ax.axis("equal")
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        else:
            st.info("No expense data for this month.")

    with chart_right:
        st.subheader("Income vs expenses")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(["Income", "Expenses"], [income, expenses])
        ax.set_ylabel("Amount (₹)")
        ax.set_title(f"{calendar.month_name[month]} {year}")
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    if category_totals:
        highest_category = max(category_totals, key=category_totals.get)
        st.info(
            f"Your highest spending category this month is **{highest_category}** "
            f"at **{money(category_totals[highest_category])}**."
        )

    if transactions:
        st.subheader("Transactions for this month")
        st.dataframe(
            [
                {
                    "ID": row[0], "Date": row[5], "Type": row[1],
                    "Category": row[3], "Payment": row[4],
                    "Amount": money(row[2]), "Description": row[6] or "",
                }
                for row in transactions
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No transactions recorded for the selected month.")
