"""
============================================================
BFF PATTERN — Core Services (Account + Transaction)
============================================================
Shared backend services used by both Web BFF and Mobile BFF.
Runs on port 9001.
"""

from flask import Flask, jsonify

app = Flask(__name__)

# ==================== Account Data ====================
accounts = {
    "acc-1": {"id": "acc-1", "name": "Main Checking", "type": "CHECKING", "balance": 15420.50, "currency": "USD", "opened": "2020-03-15"},
    "acc-2": {"id": "acc-2", "name": "Savings", "type": "SAVINGS", "balance": 52000.00, "currency": "USD", "opened": "2019-08-01"},
    "acc-3": {"id": "acc-3", "name": "Credit Card", "type": "CREDIT", "balance": -3200.75, "currency": "USD", "opened": "2021-01-10"},
}

# ==================== Transaction Data ====================
transactions = [
    {"id": "txn-1", "account_id": "acc-1", "description": "Salary Deposit", "amount": 5000.00, "type": "CREDIT", "category": "Income", "date": "2024-01-15"},
    {"id": "txn-2", "account_id": "acc-1", "description": "Grocery Store", "amount": -85.50, "type": "DEBIT", "category": "Food", "date": "2024-01-14"},
    {"id": "txn-3", "account_id": "acc-1", "description": "Electric Bill", "amount": -120.00, "type": "DEBIT", "category": "Utilities", "date": "2024-01-13"},
    {"id": "txn-4", "account_id": "acc-1", "description": "Coffee Shop", "amount": -5.75, "type": "DEBIT", "category": "Food", "date": "2024-01-13"},
    {"id": "txn-5", "account_id": "acc-2", "description": "Interest Earned", "amount": 42.50, "type": "CREDIT", "category": "Income", "date": "2024-01-12"},
    {"id": "txn-6", "account_id": "acc-1", "description": "Online Shopping", "amount": -249.99, "type": "DEBIT", "category": "Shopping", "date": "2024-01-11"},
    {"id": "txn-7", "account_id": "acc-3", "description": "Restaurant Dinner", "amount": -65.00, "type": "DEBIT", "category": "Food", "date": "2024-01-10"},
    {"id": "txn-8", "account_id": "acc-1", "description": "Freelance Payment", "amount": 1200.00, "type": "CREDIT", "category": "Income", "date": "2024-01-09"},
    {"id": "txn-9", "account_id": "acc-1", "description": "Gas Station", "amount": -45.00, "type": "DEBIT", "category": "Transport", "date": "2024-01-08"},
    {"id": "txn-10", "account_id": "acc-1", "description": "Netflix Subscription", "amount": -15.99, "type": "DEBIT", "category": "Entertainment", "date": "2024-01-07"},
]


@app.route("/accounts", methods=["GET"])
def list_accounts():
    return jsonify({"accounts": list(accounts.values())})


@app.route("/accounts/<account_id>", methods=["GET"])
def get_account(account_id):
    acc = accounts.get(account_id)
    return jsonify(acc) if acc else (jsonify({"error": "Not found"}), 404)


@app.route("/transactions", methods=["GET"])
def list_transactions():
    return jsonify({"transactions": transactions})


@app.route("/transactions/<account_id>", methods=["GET"])
def get_transactions_by_account(account_id):
    txns = [t for t in transactions if t["account_id"] == account_id]
    return jsonify({"transactions": txns, "account_id": account_id})


@app.route("/analytics/spending", methods=["GET"])
def spending_by_category():
    categories = {}
    for t in transactions:
        if t["amount"] < 0:
            cat = t["category"]
            categories[cat] = categories.get(cat, 0) + abs(t["amount"])
    
    income = sum(t["amount"] for t in transactions if t["amount"] > 0)
    expenses = sum(abs(t["amount"]) for t in transactions if t["amount"] < 0)
    
    return jsonify({
        "spending_by_category": categories,
        "total_income": income,
        "total_expenses": expenses,
        "savings_rate": round((income - expenses) / income * 100, 1) if income > 0 else 0,
    })


if __name__ == "__main__":
    print("🏦 Core Banking Services starting on port 9001...")
    print("   Endpoints: /accounts, /transactions, /analytics/spending")
    app.run(port=9001, debug=True)
