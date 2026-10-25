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

# Match the original Tkinter application's navy sidebar, pale canvas,
# white cards, purple accent, and compact dashboard spacing.
st.markdown("""
<style>
    :root { --sw-bg: #F5F7FB; --sw-navy: #172033; --sw-card: #FFFFFF;
            --sw-text: #172033; --sw-muted: #7A8499; --sw-accent: #5B5FEF;
            --sw-green: #19A974; --sw-red: #E55353; }
    .stApp { background: var(--sw-bg); color: var(--sw-text); }
    [data-testid="stHeader"] { background: rgba(245,247,251,.94); }
    [data-testid="stSidebar"] { background: var(--sw-navy); }
    [data-testid="stSidebar"] * { color: #F4F6FB; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #AAB3C5;
    }
    [data-testid="stSidebar"] hr { border-color: #2A354C; }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        background: transparent; border-radius: 8px; padding: 8px 10px;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: #293451;
    }
    .sw-greeting { font-size: 2rem; font-weight: 750; color: #172033;
                   letter-spacing: -.5px; line-height: 1.2; margin: 0; }
    .sw-subtitle { color: #7A8499; font-size: 1rem; margin-top: 7px; }
    .sw-card { background: #fff; border: 1px solid #E1E5EF; border-radius: 12px;
               display: flex; overflow: hidden; min-height: 160px;
               box-shadow: 0 2px 7px rgba(23,32,51,.025); }
    .sw-accent { width: 5px; flex: 0 0 5px; }
    .sw-card-body { padding: 19px 20px 17px; flex: 1; min-width: 0; }
    .sw-card-top { display: flex; align-items: center; gap: 12px; }
    .sw-icon { width: 44px; height: 44px; border-radius: 10px; background: #F1F2FF;
               display: flex; align-items: center; justify-content: center; font-size: 1.35rem; }
    .sw-card-label { color: #7A8499; font-size: .78rem; font-weight: 750;
                     letter-spacing: .6px; text-transform: uppercase; }
    .sw-card-value { font-size: clamp(1.35rem, 2vw, 1.9rem); font-weight: 750;
                     line-height: 1.25; margin-top: 17px; overflow-wrap: anywhere; }
    .sw-card-caption { color: #9AA3B5; font-size: .8rem; margin-top: 3px; }
    .sw-section-card { background: #fff; border: 1px solid #E1E5EF;
                       border-radius: 12px; padding: 20px 22px; }
    .sw-section-title { color: #172033; font-size: 1.25rem; font-weight: 750; margin: 0; }
    .sw-section-caption { color: #9AA3B5; font-size: .82rem; margin-top: 3px; }
    div.stButton > button[kind="primary"] {
        background: #5B5FEF; border: 0; color: white; border-radius: 8px;
        font-weight: 700; padding: .65rem 1rem;
    }
    div.stButton > button { border-radius: 8px; }
    [data-testid="stDataFrame"] { border: 1px solid #E5E8EF; border-radius: 8px; }
    @media (max-width: 800px) {
        .sw-greeting { font-size: 1.6rem; }
        .sw-card { min-height: 140px; }
        .sw-card-body { padding: 14px; }
    }
</style>
""", unsafe_allow_html=True)

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
st.sidebar.markdown(
    '<div style="font-size:1.55rem;font-weight:800;color:white;margin:5px 0 0 0;">💰 SpendWise</div>'
    '<div style="font-size:.78rem;color:#AAB3C5;margin:2px 0 22px 2px;">Smart money management</div>'
    '<hr style="border:0;border-top:1px solid #2A354C;margin:18px 0 24px;">'
    '<div style="font-size:.72rem;font-weight:800;letter-spacing:1px;color:#6F7C95;margin:0 0 8px 4px;">MAIN MENU</div>',
    unsafe_allow_html=True,
)
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "All transactions", "Analytics", "Monthly budget", "Add transaction"],
    label_visibility="collapsed",
)
st.sidebar.markdown(
    '<div style="position:relative;margin-top:25px;color:#6F7C95;font-size:.75rem;">SpendWise · Personal finance</div>',
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------
if page == "Dashboard":
    header_left, header_right = st.columns([4, 1.35], vertical_alignment="center")
    with header_left:
        st.markdown('<div class="sw-greeting">Good evening! 👋</div>', unsafe_allow_html=True)
        st.markdown('<div class="sw-subtitle">Here\'s your financial overview</div>', unsafe_allow_html=True)
    with header_right:
        if st.button("＋  Add Transaction", type="primary", use_container_width=True):
            st.session_state["dashboard_add_transaction"] = True

    if st.session_state.get("dashboard_add_transaction"):
        with st.expander("Add transaction", expanded=True):
            show_transaction_form("dashboard_add")
            if st.button("Close form", key="close_dashboard_add"):
                st.session_state["dashboard_add_transaction"] = False
                st.rerun()

    st.write("")
    income = get_total_income()
    expenses = get_total_expenses()
    balance = income - expenses

    card_specs = [
        ("TOTAL INCOME", money(income), "💰", "#19A974"),
        ("TOTAL EXPENSES", money(expenses), "💸", "#E55353"),
        ("AVAILABLE BALANCE", money(balance), "💵", "#5B5FEF"),
    ]
    card_cols = st.columns(3, gap="medium")
    for col, (label, value, icon, accent) in zip(card_cols, card_specs):
        with col:
            st.markdown(
                f'<div class="sw-card"><div class="sw-accent" style="background:{accent};"></div>'
                f'<div class="sw-card-body"><div class="sw-card-top">'
                f'<div class="sw-icon">{icon}</div><div class="sw-card-label">{label}</div></div>'
                f'<div class="sw-card-value" style="color:{accent};">{value}</div>'
                f'<div class="sw-card-caption">Current total</div></div></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    st.write("")
    transactions = get_transactions()[:8]
    recent_by_id = {str(row[0]): row for row in transactions}

    if transactions:
        action_left, action_right, spacer = st.columns([1.3, 1.45, 5])
        with action_left:
            if st.button("✏️  Edit Selected", use_container_width=True):
                selected_id = st.session_state.get("dashboard_selected_transaction")
                if selected_id in recent_by_id:
                    st.session_state["dashboard_edit_id"] = selected_id
                else:
                    st.warning("Select a transaction in the table first.")
        with action_right:
            if st.button("🗑  Delete Selected", use_container_width=True):
                selected_id = st.session_state.get("dashboard_selected_transaction")
                if selected_id in recent_by_id:
                    st.session_state["dashboard_delete_id"] = selected_id
                else:
                    st.warning("Select a transaction in the table first.")

        if st.session_state.get("dashboard_edit_id") in recent_by_id:
            edit_id = st.session_state["dashboard_edit_id"]
            with st.expander(f"Edit transaction #{edit_id}", expanded=True):
                show_transaction_form(f"dashboard_edit_{edit_id}", recent_by_id[edit_id])
                if st.button("Cancel editing", key="cancel_dashboard_edit"):
                    st.session_state.pop("dashboard_edit_id", None)
                    st.rerun()

        if st.session_state.get("dashboard_delete_id") in recent_by_id:
            delete_id = st.session_state["dashboard_delete_id"]
            st.warning(f"Delete transaction #{delete_id}? This cannot be undone.")
            yes, no = st.columns(2)
            with yes:
                if st.button("Confirm delete", type="primary", key="confirm_dashboard_delete"):
                    delete_transaction(int(delete_id))
                    st.session_state.pop("dashboard_delete_id", None)
                    st.session_state.pop("dashboard_selected_transaction", None)
                    st.rerun()
            with no:
                if st.button("Cancel", key="cancel_dashboard_delete"):
                    st.session_state.pop("dashboard_delete_id", None)
                    st.rerun()

    st.markdown(
        '<div class="sw-section-card"><div class="sw-section-title">Recent Transactions</div>'
        '<div class="sw-section-caption">Your latest financial activity</div></div>',
        unsafe_allow_html=True,
    )

    if transactions:
        st.caption("Select a transaction below to use the Edit Selected or Delete Selected buttons.")
        table_rows = [
            {
                "Select": str(row[0]) == st.session_state.get("dashboard_selected_transaction"),
                "ID": row[0], "Date": row[5], "Type": row[1],
                "Category": row[3], "Payment": row[4],
                "Amount": money(row[2]), "Description": row[6] or "",
            }
            for row in transactions
        ]
        edited_table = st.data_editor(
            table_rows,
            use_container_width=True,
            hide_index=True,
            disabled=["ID", "Date", "Type", "Category", "Payment", "Amount", "Description"],
            column_config={
                "Select": st.column_config.CheckboxColumn("Select", help="Choose a transaction"),
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Date": st.column_config.TextColumn("Date"),
                "Type": st.column_config.TextColumn("Type"),
                "Category": st.column_config.TextColumn("Category"),
                "Payment": st.column_config.TextColumn("Payment"),
                "Amount": st.column_config.TextColumn("Amount"),
                "Description": st.column_config.TextColumn("Description"),
            },
            key="dashboard_recent_table",
        )
        checked = [row for row in edited_table if row.get("Select")]
        if checked:
            st.session_state["dashboard_selected_transaction"] = str(checked[-1]["ID"])
        elif st.session_state.get("dashboard_selected_transaction") not in recent_by_id:
            st.session_state.pop("dashboard_selected_transaction", None)
    else:
        st.markdown(
            '<div class="sw-section-card"><div class="sw-section-title">Recent Transactions</div>'
            '<div class="sw-section-caption">Your latest financial activity</div>'
            '<p style="color:#9AA3B5;margin-top:18px;">No transactions yet. Add your first transaction to get started.</p></div>',
            unsafe_allow_html=True,
        )

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
