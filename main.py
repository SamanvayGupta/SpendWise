import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

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
    get_monthly_transactions
)


# ============================================================
# COLORS
# ============================================================

BG_COLOR = "#F5F7FB"
SIDEBAR_COLOR = "#172033"
CARD_COLOR = "#FFFFFF"

TEXT_COLOR = "#172033"
SECONDARY_TEXT = "#7A8499"

ACCENT_COLOR = "#5B5FEF"
GREEN_COLOR = "#19A974"
RED_COLOR = "#E55353"

BORDER_COLOR = "#E5E8EF"


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title("SpendWise - Personal Expense Tracker")

root.geometry("1200x720")

root.minsize(1000, 650)

root.configure(
    bg=BG_COLOR
)


# Create database

create_database()




# ============================================================
# TREEVIEW STYLE
# ============================================================

style = ttk.Style()

style.theme_use("clam")


style.configure(
    "Treeview",
    background=CARD_COLOR,
    foreground=TEXT_COLOR,
    fieldbackground=CARD_COLOR,
    rowheight=40,
    font=("Segoe UI", 10)
)


style.configure(
    "Treeview.Heading",
    background="#EEF0F7",
    foreground=TEXT_COLOR,
    font=("Segoe UI", 10, "bold"),
    padding=10
)


style.map(
    "Treeview",
    background=[
        ("selected", "#587996")
    ],
    foreground=[
        ("selected", "white")
    ]
)


# ============================================================
# GLOBAL VARIABLES
# ============================================================

income_label = None
expense_label = None
balance_label = None

transaction_table = None


# ============================================================
# REFRESH MAIN DASHBOARD
# ============================================================

def refresh_dashboard():

    total_income = get_total_income()

    total_expenses = get_total_expenses()

    balance = total_income - total_expenses


    income_label.config(
        text=f"₹{total_income:,.2f}"
    )


    expense_label.config(
        text=f"₹{total_expenses:,.2f}"
    )


    balance_label.config(
        text=f"₹{balance:,.2f}"
    )


    # Clear table

    for item in transaction_table.get_children():

        transaction_table.delete(item)


    # Get transactions

    transactions = get_transactions()


    # Show latest transactions

    for transaction in transactions[:8]:

        transaction_id = transaction[0]

        transaction_type = transaction[1]

        amount = transaction[2]

        category = transaction[3]

        payment_method = transaction[4]

        transaction_date = transaction[5]

        description = transaction[6]


        transaction_table.insert(
            "",
            "end",
            iid=str(transaction_id),
            values=(
                transaction_date,
                transaction_type,
                category,
                payment_method,
                f"₹{amount:,.2f}",
                description
            )
        )


# ============================================================
# DELETE TRANSACTION FROM MAIN DASHBOARD
# ============================================================

def delete_selected_transaction():

    selected = transaction_table.selection()


    if not selected:

        messagebox.showwarning(
            "No Transaction Selected",
            "Please select a transaction first."
        )

        return


    transaction_id = selected[0]


    confirm = messagebox.askyesno(
        "Delete Transaction",
        "Are you sure you want to delete this transaction?"
    )


    if confirm:

        delete_transaction(
            transaction_id
        )


        messagebox.showinfo(
            "Deleted",
            "Transaction deleted successfully."
        )


        refresh_dashboard()


# ============================================================
# EDIT TRANSACTION FROM MAIN DASHBOARD
# ============================================================

def edit_selected_transaction():

    selected = transaction_table.selection()


    if not selected:

        messagebox.showwarning(
            "No Transaction Selected",
            "Please select a transaction first."
        )

        return


    transaction_id = selected[0]


    transactions = get_transactions()


    selected_transaction = None


    for transaction in transactions:

        if str(transaction[0]) == str(transaction_id):

            selected_transaction = transaction

            break


    if selected_transaction is None:

        messagebox.showerror(
            "Error",
            "Transaction could not be found."
        )

        return


    open_edit_window(
        selected_transaction,
        root,
        refresh_dashboard
    )


# ============================================================
# EDIT WINDOW
# ============================================================

def open_edit_window(transaction, parent, refresh_function):

    window = tk.Toplevel(parent)

    window.title(
        "SpendWise - Edit Transaction"
    )

    window.geometry(
        "550x750"
    )

    window.configure(
        bg=BG_COLOR
    )

    window.resizable(
        False,
        False
    )


    # Header

    tk.Label(
        window,
        text="✏️ Edit Transaction",
        bg=BG_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 21, "bold")
    ).pack(
        pady=(25, 5)
    )


    tk.Label(
        window,
        text="Update your transaction details",
        bg=BG_COLOR,
        fg=SECONDARY_TEXT,
        font=("Segoe UI", 10)
    ).pack(
        pady=(0, 20)
    )


    # Form card

    form = tk.Frame(
        window,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    form.pack(
        padx=30,
        fill="both",
        expand=True
    )


    # -------------------------
    # Type
    # -------------------------

    tk.Label(
        form,
        text="Transaction Type",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 10, "bold")
    ).pack(
        anchor="w",
        padx=25,
        pady=(25, 5)
    )


    type_var = tk.StringVar(
        value=transaction[1]
    )


    type_box = ttk.Combobox(
        form,
        textvariable=type_var,
        values=[
            "Expense",
            "Income"
        ],
        state="readonly"
    )


    type_box.pack(
        fill="x",
        padx=25
    )


    # -------------------------
    # Amount
    # -------------------------

    tk.Label(
        form,
        text="Amount (₹)",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 10, "bold")
    ).pack(
        anchor="w",
        padx=25,
        pady=(18, 5)
    )


    amount_entry = tk.Entry(
        form,
        font=("Segoe UI", 11)
    )


    amount_entry.pack(
        fill="x",
        padx=25,
        ipady=8
    )


    amount_entry.insert(
        0,
        str(transaction[2])
    )


    # -------------------------
    # Category
    # -------------------------

    tk.Label(
        form,
        text="Category",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 10, "bold")
    ).pack(
        anchor="w",
        padx=25,
        pady=(18, 5)
    )


    category_var = tk.StringVar(
        value=transaction[3]
    )


    category_box = ttk.Combobox(
        form,
        textvariable=category_var,
        values=[
            "Food",
            "Transport",
            "Shopping",
            "Education",
            "Entertainment",
            "Bills",
            "Health",
            "Travel",
            "Other"
        ],
        state="readonly"
    )


    category_box.pack(
        fill="x",
        padx=25
    )


    # -------------------------
    # Payment
    # -------------------------

    tk.Label(
        form,
        text="Payment Method",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 10, "bold")
    ).pack(
        anchor="w",
        padx=25,
        pady=(18, 5)
    )


    payment_var = tk.StringVar(
        value=transaction[4]
    )


    payment_box = ttk.Combobox(
        form,
        textvariable=payment_var,
        values=[
            "UPI",
            "Cash",
            "Credit Card",
            "Debit Card",
            "Bank Transfer",
            "Other"
        ],
        state="readonly"
    )


    payment_box.pack(
        fill="x",
        padx=25
    )


    # -------------------------
    # Date
    # -------------------------

    tk.Label(
        form,
        text="Date",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 10, "bold")
    ).pack(
        anchor="w",
        padx=25,
        pady=(18, 5)
    )


    date_entry = tk.Entry(
        form,
        font=("Segoe UI", 11)
    )


    date_entry.pack(
        fill="x",
        padx=25,
        ipady=8
    )


    date_entry.insert(
        0,
        str(transaction[5])
    )


    # -------------------------
    # Description
    # -------------------------

    tk.Label(
        form,
        text="Description",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 10, "bold")
    ).pack(
        anchor="w",
        padx=25,
        pady=(18, 5)
    )


    description_entry = tk.Entry(
        form,
        font=("Segoe UI", 11)
    )


    description_entry.pack(
        fill="x",
        padx=25,
        ipady=8
    )


    description_entry.insert(
        0,
        transaction[6]
    )


    # -------------------------
    # Save Changes
    # -------------------------

    def save_changes():

        try:

            amount = float(
                amount_entry.get().strip()
            )

        except ValueError:

            messagebox.showerror(
                "Invalid Amount",
                "Please enter a valid amount."
            )

            return


        if amount <= 0:

            messagebox.showerror(
                "Invalid Amount",
                "Amount must be greater than zero."
            )

            return


        update_transaction(
            transaction[0],
            type_var.get(),
            amount,
            category_var.get(),
            payment_var.get(),
            date_entry.get().strip(),
            description_entry.get().strip()
        )


        messagebox.showinfo(
            "Updated",
            "Transaction updated successfully."
        )


        window.destroy()


        refresh_function()


    tk.Button(
        form,
        text="✓  Save Changes",
        bg=ACCENT_COLOR,
        fg="white",
        activebackground="#494DD1",
        activeforeground="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        bd=0,
        cursor="hand2",
        command=save_changes
    ).pack(
        fill="x",
        padx=25,
        pady=(18, 20),
        ipady=8
    )


# ============================================================
# ADD TRANSACTION WINDOW
# ============================================================

def open_add_transaction():

    window = tk.Toplevel(root)

    window.title(
        "SpendWise - Add Transaction"
    )

    window.geometry(
        "550x750"
    )

    window.configure(
        bg=BG_COLOR
    )

    window.resizable(
        False,
        False
    )


    # Header

    tk.Label(
        window,
        text="➕ Add Transaction",
        bg=BG_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 21, "bold")
    ).pack(
        pady=(25, 5)
    )


    tk.Label(
        window,
        text="Record your income or expense",
        bg=BG_COLOR,
        fg=SECONDARY_TEXT,
        font=("Segoe UI", 10)
    ).pack(
        pady=(0, 20)
    )


    # Form

    form = tk.Frame(
        window,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    form.pack(
        padx=30,
        fill="both",
        expand=True
    )


    # -------------------------
    # Type
    # -------------------------

    tk.Label(
        form,
        text="Transaction Type",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 10, "bold")
    ).pack(
        anchor="w",
        padx=25,
        pady=(25, 5)
    )


    type_var = tk.StringVar(
        value="Expense"
    )


    ttk.Combobox(
        form,
        textvariable=type_var,
        values=[
            "Expense",
            "Income"
        ],
        state="readonly"
    ).pack(
        fill="x",
        padx=25
    )


    # -------------------------
    # Amount
    # -------------------------

    tk.Label(
        form,
        text="Amount (₹)",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 10, "bold")
    ).pack(
        anchor="w",
        padx=25,
        pady=(18, 5)
    )


    amount_entry = tk.Entry(
        form,
        font=("Segoe UI", 11)
    )


    amount_entry.pack(
        fill="x",
        padx=25,
        ipady=8
    )


    # -------------------------
    # Category
    # -------------------------

    tk.Label(
        form,
        text="Category",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 10, "bold")
    ).pack(
        anchor="w",
        padx=25,
        pady=(18, 5)
    )


    category_var = tk.StringVar(
        value="Food"
    )


    ttk.Combobox(
        form,
        textvariable=category_var,
        values=[
            "Food",
            "Transport",
            "Shopping",
            "Education",
            "Entertainment",
            "Bills",
            "Health",
            "Travel",
            "Other"
        ],
        state="readonly"
    ).pack(
        fill="x",
        padx=25
    )


    # -------------------------
    # Payment
    # -------------------------

    tk.Label(
        form,
        text="Payment Method",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 10, "bold")
    ).pack(
        anchor="w",
        padx=25,
        pady=(18, 5)
    )


    payment_var = tk.StringVar(
        value="UPI"
    )


    ttk.Combobox(
        form,
        textvariable=payment_var,
        values=[
            "UPI",
            "Cash",
            "Credit Card",
            "Debit Card",
            "Bank Transfer",
            "Other"
        ],
        state="readonly"
    ).pack(
        fill="x",
        padx=25
    )


    # -------------------------
    # Date
    # -------------------------

    tk.Label(
        form,
        text="Date",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 10, "bold")
    ).pack(
        anchor="w",
        padx=25,
        pady=(18, 5)
    )


    date_entry = tk.Entry(
        form,
        font=("Segoe UI", 11)
    )


    date_entry.pack(
        fill="x",
        padx=25,
        ipady=8
    )


    date_entry.insert(
        0,
        str(date.today())
    )


    # -------------------------
    # Description
    # -------------------------

    tk.Label(
        form,
        text="Description",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 10, "bold")
    ).pack(
        anchor="w",
        padx=25,
        pady=(18, 5)
    )


    description_entry = tk.Entry(
        form,
        font=("Segoe UI", 11)
    )


    description_entry.pack(
        fill="x",
        padx=25,
        ipady=8
    )


    # -------------------------
    # Save
    # -------------------------

    def save_transaction():

        amount_text = amount_entry.get().strip()


        if not amount_text:

            messagebox.showerror(
                "Invalid Amount",
                "Please enter an amount."
            )

            return


        try:

            amount = float(amount_text)

        except ValueError:

            messagebox.showerror(
                "Invalid Amount",
                "Please enter a valid number."
            )

            return


        if amount <= 0:

            messagebox.showerror(
                "Invalid Amount",
                "Amount must be greater than zero."
            )

            return


        add_transaction(
            type_var.get(),
            amount,
            category_var.get(),
            payment_var.get(),
            date_entry.get().strip(),
            description_entry.get().strip()
        )


        messagebox.showinfo(
            "Success",
            "Transaction added successfully."
        )


        window.destroy()


        refresh_dashboard()


    tk.Button(
        form,
        text="✓  Save Transaction",
        bg=ACCENT_COLOR,
        fg="white",
        activebackground="#494DD1",
        activeforeground="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        bd=0,
        cursor="hand2",
        command=save_transaction
    ).pack(
        fill="x",
        padx=25,
        pady=(18, 20),
        ipady=8
    )

# ============================================================
# BUDGET WINDOW
# ============================================================

def open_budget_window():

    window = tk.Toplevel(root)

    window.title("SpendWise - Budget")

    window.geometry("700x800")
    

    window.configure(
        bg=BG_COLOR
    )
    
     # ========================================================
    # SCROLLABLE BUDGET WINDOW
    # ========================================================

    canvas = tk.Canvas(
        window,
        bg=BG_COLOR,
        highlightthickness=0
    )

    scrollbar = ttk.Scrollbar(
        window,
        orient="vertical",
        command=canvas.yview
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    scroll_frame = tk.Frame(
        canvas,
        bg=BG_COLOR
    )

    canvas_window = canvas.create_window(
        (0, 0),
        window=scroll_frame,
        anchor="nw"
    )


    def update_scroll_region(event=None):

        canvas.configure(
            scrollregion=canvas.bbox("all")
        )


    scroll_frame.bind(
        "<Configure>",
        update_scroll_region
    )


    def resize_scroll_frame(event):

        canvas.itemconfig(
            canvas_window,
            width=event.width
        )


    canvas.bind(
        "<Configure>",
        resize_scroll_frame
    )


    # Mouse wheel scrolling

    def mouse_wheel(event):

        canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )


    canvas.bind_all(
        "<MouseWheel>",
        mouse_wheel
    )


    # IMPORTANT:
    # From this point onward, use scroll_frame
    # instead of window for the UI elements.

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    tk.Label(
        scroll_frame,
        text="🎯 Monthly Budget",
        bg=BG_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 24, "bold")
    ).pack(
        anchor="w",
        padx=35,
        pady=(30, 5)
    )

    tk.Label(
        window,
        text="Set and monitor your monthly spending limit",
        bg=BG_COLOR,
        fg=SECONDARY_TEXT,
        font=("Segoe UI", 10)
    ).pack(
        anchor="w",
        padx=35
    )

    # --------------------------------------------------------
    # BUDGET CARD
    # --------------------------------------------------------

    card = tk.Frame(
        scroll_frame,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    card.pack(
        fill="x",
        padx=35,
        pady=25
    )

    tk.Label(
        card,
        text="Monthly Budget",
        bg=CARD_COLOR,
        fg=SECONDARY_TEXT,
        font=("Segoe UI", 10, "bold")
    ).pack(
        pady=(25, 8)
    )

    budget_entry = tk.Entry(
        card,
        font=("Segoe UI", 18),
        justify="center",
        relief="flat",
        bg="#F5F5FA"
    )

    budget_entry.pack(
        padx=30,
        pady=10,
        ipady=8
    )

    # Get existing budget

    current_budget = get_budget()

    if current_budget > 0:

        budget_entry.insert(
            0,
            str(current_budget)
        )

    # --------------------------------------------------------
    # SAVE BUDGET
    # --------------------------------------------------------

    def save():

        value = budget_entry.get().strip()

        if not value:

            messagebox.showwarning(
                "Invalid Budget",
                "Please enter a budget amount."
            )

            return

        try:

            amount = float(value)

        except ValueError:

            messagebox.showerror(
                "Invalid Budget",
                "Please enter a valid number."
            )

            return

        if amount <= 0:

            messagebox.showwarning(
                "Invalid Budget",
                "Budget must be greater than zero."
            )

            return

        save_budget(amount)

        messagebox.showinfo(
            "Budget Saved",
            "Your monthly budget has been saved successfully."
        )

        window.destroy()

    tk.Button(
        card,
        text="💾  Save Budget",
        bg=ACCENT_COLOR,
        fg="white",
        activebackground=ACCENT_COLOR,
        activeforeground="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=25,
        pady=10,
        command=save
    ).pack(
        pady=(10, 25)
    )

    # --------------------------------------------------------
    # CURRENT STATUS
    # --------------------------------------------------------

    budget = get_budget()

    today = date.today()

    current_month = today.month
    current_year = today.year

    expenses = get_monthly_expenses(
    current_month,
    current_year
)

    remaining = budget - expenses

    status_card = tk.Frame(
        scroll_frame,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    status_card.pack(
        fill="x",
        padx=35,
        pady=5
    )

    tk.Label(
        status_card,
        text="Current Status",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 13, "bold")
    ).pack(
        anchor="w",
        padx=20,
        pady=(20, 15)
    )

    tk.Label(
        status_card,
        text=f"Budget: ₹{budget:,.2f}",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 11)
    ).pack(
        anchor="w",
        padx=20,
        pady=3
    )

    tk.Label(
        status_card,
        text=f"Spent: ₹{expenses:,.2f}",
        bg=CARD_COLOR,
        fg=RED_COLOR,
        font=("Segoe UI", 11)
    ).pack(
        anchor="w",
        padx=20,
        pady=3
    )

    remaining_color = (
        GREEN_COLOR
        if remaining >= 0
        else RED_COLOR
    )

    tk.Label(
        status_card,
        text=f"Remaining: ₹{remaining:,.2f}",
        bg=CARD_COLOR,
        fg=remaining_color,
        font=("Segoe UI", 12, "bold")
    ).pack(
        anchor="w",
        padx=20,
        pady=(3, 20)
    )
    progress_card = tk.Frame(
        scroll_frame,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    progress_card.pack(
        fill="x",
        padx=35,
        pady=15
    )

    tk.Label(
        progress_card,
        text="Budget Usage",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 13, "bold")
    ).pack(
        anchor="w",
        padx=20,
        pady=(18, 8)
    )

    if budget > 0:
        percentage = (expenses / budget) * 100
    else:
        percentage = 0

    progress_value = min(percentage, 100)

    progress = ttk.Progressbar(
        progress_card,
        orient="horizontal",
        length=400,
        mode="determinate"
    )

    progress["value"] = progress_value

    progress.pack(
        fill="x",
        padx=20,
        pady=10
    )

    tk.Label(
        progress_card,
        text=f"{percentage:.1f}% of your budget used",
        bg=CARD_COLOR,
        fg=SECONDARY_TEXT,
        font=("Segoe UI", 10)
    ).pack(
        anchor="w",
        padx=20,
        pady=(0, 15)
    )

    if percentage >= 100:
        warning_text = "🚨 You have exceeded your monthly budget!"
    elif percentage >= 80:
        warning_text = "⚠️ You have used more than 80% of your budget."
    elif percentage >= 50:
        warning_text = "💡 You have used more than half of your budget."
    else:
        warning_text = "✅ You are comfortably within your budget."

    tk.Label(
        progress_card,
        text=warning_text,
        bg=CARD_COLOR,
        fg=RED_COLOR if percentage >= 80 else GREEN_COLOR,
        font=("Segoe UI", 10, "bold")
    ).pack(
        pady=(0, 18)
    )
    
# ============================================================
# ANALYTICS WINDOW
# ============================================================

def open_analytics_window(selected_month=None, selected_year=None):

    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    window = tk.Toplevel(root)

    window.title("SpendWise - Analytics")

    window.geometry("1200x800")

    window.configure(
        bg=BG_COLOR
    )
    # ========================================================
    # SCROLLABLE ANALYTICS WINDOW
    # ========================================================

    canvas = tk.Canvas(
        window,
        bg=BG_COLOR,
        highlightthickness=0
    )

    scrollbar = ttk.Scrollbar(
        window,
        orient="vertical",
        command=canvas.yview
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    analytics_frame = tk.Frame(
        canvas,
        bg=BG_COLOR
    )

    canvas_window = canvas.create_window(
        (0, 0),
        window=analytics_frame,
        anchor="nw"
    )

    def update_scroll():
        canvas.configure(
            scrollregion=canvas.bbox("all")
        )

    analytics_frame.bind(
        "<Configure>",
        lambda event: update_scroll()
    )

    def resize_frame(event):
        canvas.itemconfig(
            canvas_window,
            width=event.width
        )

    canvas.bind(
        "<Configure>",
        resize_frame
    )

    def mouse_wheel(event):
        canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    canvas.bind_all(
        "<MouseWheel>",
        mouse_wheel
    )
    # --------------------------------------------------------
    # GET DATA - SELECTED MONTH
    # --------------------------------------------------------

    today = date.today()

    if selected_month is None:
        selected_month = today.month

    if selected_year is None:
        selected_year = today.year
    
    month_names = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ]
    transactions = get_monthly_transactions(
        selected_month,
        selected_year
    )

    total_income = get_monthly_income(
        selected_month,
        selected_year
    )

    total_expenses = get_monthly_expenses(
        selected_month,
        selected_year
    )

    balance = total_income - total_expenses


    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    header = tk.Frame(
        analytics_frame,
        bg=BG_COLOR
    )

    header.pack(
        fill="x",
        padx=35,
        pady=(25, 10)
    )


    tk.Label(
        header,
        text="📊 Financial Analytics",
        bg=BG_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 24, "bold")
    ).pack(
        anchor="w"
    )


    tk.Label(
        header,
        text="Understand your spending habits and financial health",
        bg=BG_COLOR,
        fg=SECONDARY_TEXT,
        font=("Segoe UI", 10)
    ).pack(
        anchor="w",
        pady=(4, 0)
    )
    tk.Label(
    header,
    text=f"Showing data for {month_names[selected_month - 1]} {selected_year}",
    bg=BG_COLOR,
    fg=ACCENT_COLOR,
    font=("Segoe UI", 10, "bold")
    ).pack(
    anchor="w",
    pady=(5, 0)
    )
    
    # --------------------------------------------------------
    # MONTH AND YEAR FILTER
    # --------------------------------------------------------

    filter_frame = tk.Frame(
        header,
        bg=BG_COLOR
    )

    filter_frame.pack(
        anchor="w",
        pady=(15, 5)
    )

    # Month
    tk.Label(
       filter_frame,
       text="Month:",
       bg=BG_COLOR,
       fg=TEXT_COLOR,
       font=("Segoe UI", 10, "bold")
    ).pack(
       side="left",
       padx=(0, 5)
    )

    month_var = tk.StringVar(
        value=month_names[selected_month - 1]
    )

    month_dropdown = ttk.Combobox(
       filter_frame,
       textvariable=month_var,
       values=month_names,
       state="readonly",
       width=12
     )

    month_dropdown.pack(
       side="left",
       padx=(0, 15)
    )

    # Year
    tk.Label(
       filter_frame,
       text="Year:",
       bg=BG_COLOR,
       fg=TEXT_COLOR,
       font=("Segoe UI", 10, "bold")
    ).pack(
       side="left",
      padx=(0, 5)
    )

    year_var = tk.StringVar(
       value=str(selected_year)
    )

    year_list = [
       str(year)
     for year in range(
        today.year - 5,
        today.year + 1
    )
    ]

    year_dropdown = ttk.Combobox(
    filter_frame,
    textvariable=year_var,
    values=year_list,
    state="readonly",
    width=8
   )

    year_dropdown.pack(
    side="left",
    padx=(0, 15)
    )


    def apply_analytics_filter():

        new_month = month_names.index(
        month_var.get()
        ) + 1

        new_year = int(
        year_var.get()
       )

        window.destroy()

        open_analytics_window(
        new_month,
        new_year
    )


    tk.Button(
    filter_frame,
    text="🔎 Apply Filter",
    bg=ACCENT_COLOR,
    fg="white",
    activebackground="#494DD1",
    activeforeground="white",
    font=("Segoe UI", 9, "bold"),
    relief="flat",
    bd=0,
    cursor="hand2",
    command=apply_analytics_filter
    ).pack(
    side="left",
    ipady=5,
    padx=5
    )

    # --------------------------------------------------------
    # SUMMARY CARDS
    # --------------------------------------------------------

    cards = tk.Frame(
        analytics_frame,
        bg=BG_COLOR
    )

    cards.pack(
        fill="x",
        padx=30,
        pady=15
    )


    def analytics_card(
        title,
        value,
        icon,
        value_color
    ):

        card = tk.Frame(
            cards,
            bg=CARD_COLOR,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )

        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )


        tk.Label(
            card,
            text=icon,
            bg=CARD_COLOR,
            font=("Segoe UI Emoji", 20)
        ).pack(
            pady=(15, 5)
        )


        tk.Label(
            card,
            text=title,
            bg=CARD_COLOR,
            fg=SECONDARY_TEXT,
            font=("Segoe UI", 9, "bold")
        ).pack()


        tk.Label(
            card,
            text=value,
            bg=CARD_COLOR,
            fg=value_color,
            font=("Segoe UI", 19, "bold")
        ).pack(
            pady=(5, 15)
        )


    analytics_card(
        "Total Income",
        f"₹{total_income:,.2f}",
        "💰",
        GREEN_COLOR
    )


    analytics_card(
        "Total Expenses",
        f"₹{total_expenses:,.2f}",
        "💸",
        RED_COLOR
    )


    analytics_card(
        "Available Balance",
        f"₹{balance:,.2f}",
        "💵",
        ACCENT_COLOR
    )


    # --------------------------------------------------------
    # SAVINGS RATE
    # --------------------------------------------------------

    if total_income > 0:

        savings_rate = (
            balance / total_income
        ) * 100

    else:

        savings_rate = 0


    analytics_card(
        "Savings Rate",
        f"{savings_rate:.1f}%",
        "📈",
        ACCENT_COLOR
    )


    # --------------------------------------------------------
    # CHART AREA
    # --------------------------------------------------------

    chart_area = tk.Frame(
        analytics_frame,
        bg=BG_COLOR
    )

    chart_area.pack(
        fill="both",
        padx=30,
        pady=10
    )


    # ========================================================
    # EXPENSE BY CATEGORY
    # ========================================================

    category_data = {}


    for transaction in transactions:

        transaction_type = transaction[1]

        amount = transaction[2]

        category = transaction[3]


        if transaction_type == "Expense":

            if category not in category_data:

                category_data[category] = 0


            category_data[category] += amount


    # Create left chart card

    pie_card = tk.Frame(
        chart_area,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    pie_card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=5
    )


    tk.Label(
        pie_card,
        text="Expenses by Category",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 13, "bold")
    ).pack(
        pady=(12, 0)
    )


    fig1, ax1 = plt.subplots(
        figsize=(5, 4)
    )


    if category_data:

        ax1.pie(
            category_data.values(),
            labels=category_data.keys(),
            autopct="%1.1f%%"
        )

        ax1.set_title(
            "Where your money goes"
        )

    else:

        ax1.text(
            0.5,
            0.5,
            "No expense data available",
            ha="center",
            va="center"
        )

        ax1.axis("off")


    fig1.tight_layout()


    canvas1 = FigureCanvasTkAgg(
        fig1,
        master=pie_card
    )

    canvas1.draw()

    canvas1.get_tk_widget().pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )


    # ========================================================
    # INCOME VS EXPENSE
    # ========================================================

    bar_card = tk.Frame(
        chart_area,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    bar_card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=5
    )


    tk.Label(
        bar_card,
        text="Income vs Expenses",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 13, "bold")
    ).pack(
        pady=(12, 0)
    )


    fig2, ax2 = plt.subplots(
        figsize=(5, 4)
    )


    ax2.bar(
        ["Income", "Expenses"],
        [
            total_income,
            total_expenses
        ]
    )


    ax2.set_ylabel(
        "Amount (₹)"
    )


    ax2.set_title(
        "Financial Overview"
    )


    fig2.tight_layout()


    canvas2 = FigureCanvasTkAgg(
        fig2,
        master=bar_card
    )

    canvas2.draw()

    canvas2.get_tk_widget().pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )


    # --------------------------------------------------------
    # INSIGHTS
    # --------------------------------------------------------

    insights = tk.Frame(
        analytics_frame,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    insights.pack(
        fill="x",
        padx=35,
        pady=(5, 25)
    )


    tk.Label(
        insights,
        text="💡 Spending Insight",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 12, "bold")
    ).pack(
        anchor="w",
        padx=20,
        pady=(15, 5)
    )


    if category_data:

        highest_category = max(
            category_data,
            key=category_data.get
        )

        highest_amount = category_data[
            highest_category
        ]


        insight_text = (
            f"Your highest spending category is "
            f"{highest_category} "
            f"with ₹{highest_amount:,.2f}."
        )

    else:

        insight_text = (
            "Add some expense transactions "
            "to see spending insights."
        )


    tk.Label(
        insights,
        text=insight_text,
        bg=CARD_COLOR,
        fg=SECONDARY_TEXT,
        font=("Segoe UI", 10)
    ).pack(
        anchor="w",
        padx=20,
        pady=(0, 15)
    )

# ============================================================
# TRANSACTIONS WINDOW
# ============================================================

def open_transactions_window():

    window = tk.Toplevel(root)

    window.title(
        "SpendWise - All Transactions"
    )

    window.geometry(
        "1150x800"
    )

    window.configure(
        bg=BG_COLOR
    )


    # ========================================================
    # HEADER
    # ========================================================

    header = tk.Frame(
        window,
        bg=BG_COLOR
    )

    header.pack(
        fill="x",
        padx=30,
        pady=(25, 15)
    )


    tk.Label(
        header,
        text="📋 All Transactions",
        bg=BG_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 23, "bold")
    ).pack(
        side="left"
    )


    # ========================================================
    # FILTER CARD
    # ========================================================

    filter_card = tk.Frame(
        window,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    filter_card.pack(
        fill="x",
        padx=30,
        pady=5
    )


    # Search

    tk.Label(
        filter_card,
        text="🔎 Search",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 9, "bold")
    ).grid(
        row=0,
        column=0,
        padx=(20, 5),
        pady=(15, 5),
        sticky="w"
    )


    search_entry = tk.Entry(
        filter_card,
        width=25,
        font=("Segoe UI", 10)
    )


    search_entry.grid(
        row=1,
        column=0,
        padx=(20, 10),
        pady=(0, 15),
        ipady=6
    )


    # Type

    tk.Label(
        filter_card,
        text="Type",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 9, "bold")
    ).grid(
        row=0,
        column=1,
        padx=10,
        pady=(15, 5),
        sticky="w"
    )


    type_var = tk.StringVar(
        value="All"
    )


    ttk.Combobox(
        filter_card,
        textvariable=type_var,
        values=[
            "All",
            "Income",
            "Expense"
        ],
        state="readonly",
        width=15
    ).grid(
        row=1,
        column=1,
        padx=10,
        pady=(0, 15),
        ipady=5
    )


    # Category

    tk.Label(
        filter_card,
        text="Category",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 9, "bold")
    ).grid(
        row=0,
        column=2,
        padx=10,
        pady=(15, 5),
        sticky="w"
    )


    category_var = tk.StringVar(
        value="All"
    )


    ttk.Combobox(
        filter_card,
        textvariable=category_var,
        values=[
            "All",
            "Food",
            "Transport",
            "Shopping",
            "Education",
            "Entertainment",
            "Bills",
            "Health",
            "Travel",
            "Other"
        ],
        state="readonly",
        width=15
    ).grid(
        row=1,
        column=2,
        padx=10,
        pady=(0, 15),
        ipady=5
    )


    # ========================================================
    # TABLE CARD
    # ========================================================

    table_card = tk.Frame(
        window,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    table_card.pack(
        fill="both",
        expand=False,
        padx=30,
        pady=10
    )
    
    table_card.config(
    height=430
)

    table_card.pack_propagate(False)

    table_frame = tk.Frame(
        table_card,
        bg=CARD_COLOR
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=15
    )


    columns = (
        "ID",
        "Date",
        "Type",
        "Category",
        "Payment",
        "Amount",
        "Description"
    )


    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )


    widths = {
        "ID": 50,
        "Date": 110,
        "Type": 100,
        "Category": 130,
        "Payment": 120,
        "Amount": 110,
        "Description": 300
    }


    for column in columns:

        table.heading(
            column,
            text=column
        )

        table.column(
            column,
            width=widths[column],
            anchor="center"
        )


    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview
    )


    table.configure(
        yscrollcommand=scrollbar.set
    )


    table.pack(
        side="left",
        fill="both",
        expand=True
    )


    scrollbar.pack(
        side="right",
        fill="y"
    )


    # ========================================================
    # LOAD TABLE
    # ========================================================

    def load_transactions():

        for item in table.get_children():

            table.delete(item)


        transactions = search_transactions(
            search_entry.get().strip(),
            type_var.get(),
            category_var.get()
        )


        for transaction in transactions:

            table.insert(
                "",
                "end",
                iid=str(transaction[0]),
                values=(
                    transaction[0],
                    transaction[5],
                    transaction[1],
                    transaction[3],
                    transaction[4],
                    f"₹{transaction[2]:,.2f}",
                    transaction[6]
                )
            )


    # ========================================================
    # FILTER BUTTON
    # ========================================================

    tk.Button(
        filter_card,
        text="🔎 Apply Filter",
        bg=ACCENT_COLOR,
        fg="white",
        activebackground="#494DD1",
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        bd=0,
        cursor="hand2",
        command=load_transactions
    ).grid(
        row=1,
        column=3,
        padx=15,
        pady=(0, 15),
        ipady=5
    )


    # ========================================================
    # CLEAR FILTER
    # ========================================================

    def clear_filters():

        search_entry.delete(
            0,
            tk.END
        )

        type_var.set(
            "All"
        )

        category_var.set(
            "All"
        )

        load_transactions()


    tk.Button(
        filter_card,
        text="Clear",
        bg="#EEF0F7",
        fg=TEXT_COLOR,
        activebackground="#E1E4ED",
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        bd=0,
        cursor="hand2",
        command=clear_filters
    ).grid(
        row=1,
        column=4,
        padx=(0, 20),
        pady=(0, 15),
        ipady=5
    )


    # ========================================================
    # EDIT FROM TRANSACTIONS WINDOW
    # ========================================================

    def edit_from_transactions():

        selected = table.selection()


        if not selected:

            messagebox.showwarning(
                "No Selection",
                "Please select a transaction."
            )

            return


        transaction_id = selected[0]


        transactions = get_transactions()


        selected_transaction = None


        for transaction in transactions:

            if str(transaction[0]) == str(transaction_id):

                selected_transaction = transaction

                break


        if selected_transaction:

            open_edit_window(
                selected_transaction,
                window,
                load_transactions
            )


    # ========================================================
    # DELETE FROM TRANSACTIONS WINDOW
    # ========================================================

    def delete_from_transactions():

        selected = table.selection()


        if not selected:

            messagebox.showwarning(
                "No Selection",
                "Please select a transaction."
            )

            return


        transaction_id = selected[0]


        confirm = messagebox.askyesno(
            "Delete Transaction",
            "Are you sure you want to delete this transaction?"
        )


        if confirm:

            delete_transaction(
                transaction_id
            )


            messagebox.showinfo(
                "Deleted",
                "Transaction deleted successfully."
            )


            load_transactions()


            refresh_dashboard()


    # ========================================================
    # ACTION BUTTONS
    # ========================================================

    action_frame = tk.Frame(
        window,
        bg=BG_COLOR
    )


    action_frame.pack(
        fill="x",
        padx=30,
        pady=(0, 15)
    )


    tk.Button(
        action_frame,
        text="✏️  Edit Selected",
        bg="#EEF0FF",
        fg=ACCENT_COLOR,
        activebackground="#E2E4FF",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=15,
        pady=8,
        command=edit_from_transactions
    ).pack(
        side="right",
        padx=5
    )


    tk.Button(
        action_frame,
        text="🗑  Delete Selected",
        bg="#FFF0F0",
        fg=RED_COLOR,
        activebackground="#FFE1E1",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=15,
        pady=8,
        command=delete_from_transactions
    ).pack(
        side="right",
        padx=5
    )


    # Load initially

    load_transactions()


# ============================================================
# SIDEBAR
# ============================================================

sidebar = tk.Frame(
    root,
    bg=SIDEBAR_COLOR,
    width=260
)


sidebar.pack(
    side="left",
    fill="y"
)


sidebar.pack_propagate(
    False
)


# ============================================================
# LOGO
# ============================================================

logo_frame = tk.Frame(
    sidebar,
    bg=SIDEBAR_COLOR
)


logo_frame.pack(
    pady=(35, 10),
    padx=20,
    anchor="w"
)


tk.Label(
    logo_frame,
    text="💰",
    bg=SIDEBAR_COLOR,
    fg="white",
    font=("Segoe UI Emoji", 23)
).pack(
    side="left"
)


tk.Label(
    logo_frame,
    text="SpendWise",
    bg=SIDEBAR_COLOR,
    fg="white",
    font=("Segoe UI", 18, "bold")
).pack(
    side="left",
    padx=8
)


tk.Label(
    sidebar,
    text="Smart money management",
    bg=SIDEBAR_COLOR,
    fg="#AAB3C5",
    font=("Segoe UI", 9)
).pack(
    padx=20,
    anchor="w"
)


# Separator

tk.Frame(
    sidebar,
    bg="#2A354C",
    height=1
).pack(
    fill="x",
    padx=20,
    pady=30
)


# ============================================================
# MAIN MENU
# ============================================================

tk.Label(
    sidebar,
    text="MAIN MENU",
    bg=SIDEBAR_COLOR,
    fg="#6F7C95",
    font=("Segoe UI", 9, "bold")
).pack(
    padx=25,
    anchor="w",
    pady=(0, 10)
)


def sidebar_button(text, active=False):

    button = tk.Button(
        sidebar,
        text=text,
        bg="#293451" if active else SIDEBAR_COLOR,
        fg="white" if active else "#AAB3C5",
        activebackground="#293451",
        activeforeground="white",
        relief="flat",
        bd=0,
        anchor="w",
        font=("Segoe UI", 11, "bold"),
        padx=25,
        pady=13,
        cursor="hand2"
    )


    button.pack(
        fill="x",
        padx=12,
        pady=3
    )


    return button


dashboard_button = sidebar_button(
    "  🏠   Dashboard",
    True
)


transactions_button = sidebar_button(
    "  📋   Transactions"
)


transactions_button.config(
    command=open_transactions_window
)


analytics_button = sidebar_button(
    "  📊   Analytics"
)

analytics_button.config(
    command=open_analytics_window
)


budget_button = sidebar_button(
    "  🎯   Budget"
)

budget_button.config(
    command=open_budget_window
)

# ============================================================
# MAIN AREA - PREMIUM SCROLLABLE DASHBOARD
# ============================================================

main_area = tk.Frame(
    root,
    bg=BG_COLOR
)

main_area.pack(
    side="left",
    fill="both",
    expand=True
)


# ============================================================
# SCROLLABLE DASHBOARD
# ============================================================

dashboard_canvas = tk.Canvas(
    main_area,
    bg=BG_COLOR,
    highlightthickness=0,
    bd=0
)

dashboard_scrollbar = ttk.Scrollbar(
    main_area,
    orient="vertical",
    command=dashboard_canvas.yview
)

dashboard_canvas.configure(
    yscrollcommand=dashboard_scrollbar.set
)

dashboard_scrollbar.pack(
    side="right",
    fill="y"
)

dashboard_canvas.pack(
    side="left",
    fill="both",
    expand=True
)


dashboard_frame = tk.Frame(
    dashboard_canvas,
    bg=BG_COLOR
)

dashboard_window = dashboard_canvas.create_window(
    (0, 0),
    window=dashboard_frame,
    anchor="nw"
)


def update_dashboard_scroll(event=None):

    dashboard_canvas.configure(
        scrollregion=dashboard_canvas.bbox("all")
    )


dashboard_frame.bind(
    "<Configure>",
    update_dashboard_scroll
)


def resize_dashboard(event):

    dashboard_canvas.itemconfig(
        dashboard_window,
        width=event.width
    )


dashboard_canvas.bind(
    "<Configure>",
    resize_dashboard
)


def dashboard_mousewheel(event):

    dashboard_canvas.yview_scroll(
        int(-1 * (event.delta / 120)),
        "units"
    )


dashboard_canvas.bind_all(
    "<MouseWheel>",
    dashboard_mousewheel
)


# ============================================================
# DASHBOARD HEADER
# ============================================================

header = tk.Frame(
    dashboard_frame,
    bg=BG_COLOR
)

header.pack(
    fill="x",
    padx=40,
    pady=(30, 15)
)


# Left side of header

heading_frame = tk.Frame(
    header,
    bg=BG_COLOR
)

heading_frame.pack(
    side="left"
)


tk.Label(
    heading_frame,
    text="Good evening! 👋",
    bg=BG_COLOR,
    fg=TEXT_COLOR,
    font=("Segoe UI", 26, "bold")
).pack(
    anchor="w"
)


tk.Label(
    heading_frame,
    text="Here's your financial overview",
    bg=BG_COLOR,
    fg=SECONDARY_TEXT,
    font=("Segoe UI", 11)
).pack(
    anchor="w",
    pady=(5, 0)
)


# Add transaction button

add_transaction_button = tk.Button(
    header,
    text="＋  Add Transaction",
    bg=ACCENT_COLOR,
    fg="white",
    activebackground="#494DD1",
    activeforeground="white",
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    bd=0,
    padx=22,
    pady=13,
    cursor="hand2",
    command=open_add_transaction
)

add_transaction_button.pack(
    side="right",
    pady=5
)


# ============================================================
# SUMMARY CARDS
# ============================================================

cards_frame = tk.Frame(
    dashboard_frame,
    bg=BG_COLOR
)

cards_frame.pack(
    fill="x",
    padx=34,
    pady=(5, 18)
)


def create_card(
    parent,
    title,
    amount,
    icon,
    value_color
):

    card = tk.Frame(
        parent,
        bg=CARD_COLOR,
        highlightbackground="#E1E5EF",
        highlightthickness=1
    )

    card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=7,
        pady=3
    )


    # Colored accent strip

    accent = tk.Frame(
        card,
        bg=value_color,
        width=5
    )

    accent.pack(
        side="left",
        fill="y"
    )


    # Main card content

    card_content = tk.Frame(
        card,
        bg=CARD_COLOR
    )

    card_content.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=18
    )


    # Top row

    top = tk.Frame(
        card_content,
        bg=CARD_COLOR
    )

    top.pack(
        fill="x"
    )


    # Icon container

    icon_box = tk.Frame(
        top,
        bg="#F1F2FF",
        width=44,
        height=44
    )

    icon_box.pack(
        side="left"
    )

    icon_box.pack_propagate(False)


    tk.Label(
        icon_box,
        text=icon,
        bg="#F1F2FF",
        fg=value_color,
        font=("Segoe UI Emoji", 18)
    ).pack(
        expand=True
    )


    # Title

    tk.Label(
        top,
        text=title.upper(),
        bg=CARD_COLOR,
        fg=SECONDARY_TEXT,
        font=("Segoe UI", 9, "bold")
    ).pack(
        side="left",
        padx=12
    )


    # Amount

    label = tk.Label(
        card_content,
        text=amount,
        bg=CARD_COLOR,
        fg=value_color,
        font=("Segoe UI", 24, "bold")
    )

    label.pack(
        anchor="w",
        pady=(16, 2)
    )


    # Small description

    tk.Label(
        card_content,
        text="Current total",
        bg=CARD_COLOR,
        fg="#9AA3B5",
        font=("Segoe UI", 9)
    ).pack(
        anchor="w"
    )


    return label


income_label = create_card(
    cards_frame,
    "Total Income",
    "₹0.00",
    "💰",
    GREEN_COLOR
)


expense_label = create_card(
    cards_frame,
    "Total Expenses",
    "₹0.00",
    "💸",
    RED_COLOR
)


balance_label = create_card(
    cards_frame,
    "Available Balance",
    "₹0.00",
    "💵",
    ACCENT_COLOR
)


# ============================================================
# DASHBOARD CONTENT
# ============================================================

content = tk.Frame(
    dashboard_frame,
    bg=BG_COLOR
)

content.pack(
    fill="x",
    padx=34,
    pady=(0, 30)
)


# ============================================================
# ACTION BUTTONS
# ============================================================

action_frame = tk.Frame(
    content,
    bg=BG_COLOR
)

action_frame.pack(
    fill="x",
    pady=(0, 10)
)


delete_button = tk.Button(
    action_frame,
    text="🗑  Delete Selected",
    bg="#FFF1F1",
    fg=RED_COLOR,
    activebackground="#FFE3E3",
    activeforeground=RED_COLOR,
    font=("Segoe UI", 9, "bold"),
    relief="flat",
    bd=0,
    cursor="hand2",
    padx=15,
    pady=9,
    command=delete_selected_transaction
)

delete_button.pack(
    side="right",
    padx=(5, 0)
)


edit_button = tk.Button(
    action_frame,
    text="✏️  Edit Selected",
    bg="#F0F1FF",
    fg=ACCENT_COLOR,
    activebackground="#E3E5FF",
    activeforeground=ACCENT_COLOR,
    font=("Segoe UI", 9, "bold"),
    relief="flat",
    bd=0,
    cursor="hand2",
    padx=15,
    pady=9,
    command=edit_selected_transaction
)

edit_button.pack(
    side="right",
    padx=5
)


# ============================================================
# RECENT TRANSACTIONS CARD
# ============================================================

transactions_card = tk.Frame(
    content,
    bg=CARD_COLOR,
    highlightbackground="#E1E5EF",
    highlightthickness=1
)

transactions_card.pack(
    fill="x",
    pady=(0, 15)
)


# Header

transaction_header = tk.Frame(
    transactions_card,
    bg=CARD_COLOR
)

transaction_header.pack(
    fill="x",
    padx=22,
    pady=(18, 12)
)


tk.Label(
    transaction_header,
    text="Recent Transactions",
    bg=CARD_COLOR,
    fg=TEXT_COLOR,
    font=("Segoe UI", 16, "bold")
).pack(
    side="left"
)


tk.Label(
    transaction_header,
    text="Your latest financial activity",
    bg=CARD_COLOR,
    fg="#9AA3B5",
    font=("Segoe UI", 9)
).pack(
    side="left",
    padx=15,
    pady=(3, 0)
)


# Table

table_frame = tk.Frame(
    transactions_card,
    bg=CARD_COLOR
)

table_frame.pack(
    fill="x",
    padx=22,
    pady=(0, 20)
)


columns = (
    "Date",
    "Type",
    "Category",
    "Payment",
    "Amount",
    "Description"
)


transaction_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=7
)


column_widths = {
    "Date": 110,
    "Type": 100,
    "Category": 130,
    "Payment": 110,
    "Amount": 120,
    "Description": 240
}


for column in columns:

    transaction_table.heading(
        column,
        text=column
    )

    transaction_table.column(
        column,
        width=column_widths[column],
        anchor="center"
    )


scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=transaction_table.yview
)


transaction_table.configure(
    yscrollcommand=scrollbar.set
)


transaction_table.pack(
    side="left",
    fill="x",
    expand=True
)


scrollbar.pack(
    side="right",
    fill="y"
)


# ============================================================
# DASHBOARD FOOTER SPACE
# ============================================================

tk.Frame(
    dashboard_frame,
    bg=BG_COLOR,
    height=20
).pack(
    fill="x"
)

# ============================================================
# START APPLICATION
# ============================================================

refresh_dashboard()


root.mainloop()