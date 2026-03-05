"""
============================================================
BFF PATTERN — Mobile BFF (Compact Mobile Backend)
============================================================
Tailored backend for the mobile app. Returns compact, minimal 
responses optimized for small screens and slow networks.
Runs on port 9003.
"""

from flask import Flask, jsonify
import requests

app = Flask(__name__)
CORE_URL = "http://localhost:9001"


@app.route("/mobile/dashboard", methods=["GET"])
def mobile_dashboard():
    """
    Compact dashboard for mobile frontend.
    Returns MINIMAL data: balance summary, last 5 transactions, quick actions.
    """
    dashboard = {"served_by": "MOBILE_BFF", "platform": "mobile"}
    
    # Compact balance summary (just name + balance)
    accounts_resp = requests.get(f"{CORE_URL}/accounts").json()
    accounts = accounts_resp["accounts"]
    total_balance = sum(a["balance"] for a in accounts)
    
    dashboard["balances"] = [{"name": a["name"], "balance": f"${a['balance']:,.2f}"} for a in accounts]
    dashboard["total"] = f"${total_balance:,.2f}"
    
    # Only last 5 transactions (mobile screen is small)
    txn_resp = requests.get(f"{CORE_URL}/transactions").json()
    recent = txn_resp["transactions"][:5]
    dashboard["recent_transactions"] = [{
        "desc": t["description"][:20] + "…" if len(t["description"]) > 20 else t["description"],
        "amount": f"${t['amount']:,.2f}",
        "date": t["date"],
    } for t in recent]
    
    # Quick actions for mobile UI
    dashboard["quick_actions"] = [
        {"label": "Transfer", "icon": "transfer"},
        {"label": "Pay Bills", "icon": "bill"},
        {"label": "Deposit", "icon": "deposit"},
    ]
    
    # Mobile-specific features
    dashboard["mobile_features"] = {
        "push_notification_token": "fcm-token-abc123",
        "biometric_enabled": True,
        "offline_cache_ttl": 300,
    }
    
    return jsonify(dashboard)


if __name__ == "__main__":
    print("📱 Mobile BFF starting on port 9003...")
    print("   Compact data for mobile app")
    app.run(port=9003, debug=True)
