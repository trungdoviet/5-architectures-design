"""
============================================================
BFF PATTERN — Web BFF (Rich Dashboard Backend)
============================================================
Tailored backend for the web dashboard. Returns rich, detailed
responses with analytics data optimized for large screens.
Runs on port 9002.
"""

from flask import Flask, jsonify
import requests

app = Flask(__name__)
CORE_URL = "http://localhost:9001"


@app.route("/web/dashboard", methods=["GET"])
def web_dashboard():
    """
    Aggregated dashboard for web frontend.
    Returns RICH data: full transaction history, analytics charts, detailed accounts.
    """
    dashboard = {"served_by": "WEB_BFF", "platform": "web"}
    
    # Full account details
    accounts_resp = requests.get(f"{CORE_URL}/accounts").json()
    accounts = accounts_resp["accounts"]
    total_balance = sum(a["balance"] for a in accounts)
    
    dashboard["accounts"] = [{
        "id": a["id"],
        "name": a["name"],
        "type": a["type"],
        "balance": f"${a['balance']:,.2f}",
        "currency": a["currency"],
        "opened": a.get("opened", "N/A"),
    } for a in accounts]
    dashboard["total_balance"] = f"${total_balance:,.2f}"
    
    # Full transaction history for data tables
    txn_resp = requests.get(f"{CORE_URL}/transactions").json()
    dashboard["transaction_history"] = [{
        "id": t["id"],
        "description": t["description"],
        "amount": f"${t['amount']:,.2f}",
        "type": t["type"],
        "category": t["category"],
        "date": t["date"],
        "account_id": t["account_id"],
    } for t in txn_resp["transactions"]]
    
    # Analytics for charts
    analytics_resp = requests.get(f"{CORE_URL}/analytics/spending").json()
    dashboard["analytics"] = {
        "spending_by_category": {k: f"${v:,.2f}" for k, v in analytics_resp["spending_by_category"].items()},
        "monthly_income": f"${analytics_resp['total_income']:,.2f}",
        "monthly_expenses": f"${analytics_resp['total_expenses']:,.2f}",
        "savings_rate": f"{analytics_resp['savings_rate']}%",
        "chart_type": "pie_chart",
    }
    
    # Web-specific features
    dashboard["features"] = {
        "export_to_csv": True,
        "date_range_filter": True,
        "advanced_search": True,
        "multi_account_view": True,
    }
    
    return jsonify(dashboard)


if __name__ == "__main__":
    print("🖥️  Web BFF starting on port 9002...")
    print("   Rich dashboard data for web frontend")
    app.run(port=9002, debug=True)
