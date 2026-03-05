"""
============================================================
STRANGLER FIG PATTERN — Facade Router (Proxy)
============================================================

This is the CORE of the Strangler Fig Pattern.

The Facade Router sits in front of both the legacy monolith
and the new microservice(s). It routes incoming requests to
the appropriate backend based on feature flags.

Runs on port 5000 — this is the only URL clients know about.

Routing Rules:
  /api/orders   → New Order Service (port 5002) when flag is ON
  /api/orders   → Legacy Monolith (port 5001) when flag is OFF
  /api/inventory → Always → Legacy Monolith (not yet migrated)
  /api/payments  → Always → Legacy Monolith (not yet migrated)
"""

from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Service URLs
MONOLITH_URL = os.getenv("MONOLITH_URL", "http://localhost:5001")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://localhost:5002")

# Feature flags — In production, use a feature flag service (LaunchDarkly, Unleash, etc.)
feature_flags = {
    "orders.use_new_service": True,  # Toggle this to switch between old and new
}


def get_flag(flag_name):
    return feature_flags.get(flag_name, False)


# ==================== ORDER ROUTES (Conditional routing) ====================

@app.route("/api/orders", methods=["GET", "POST"])
def proxy_orders():
    if get_flag("orders.use_new_service"):
        target_url = f"{ORDER_SERVICE_URL}/api/orders"
        print(f"🔀 Routing /api/orders → NEW Order Service ({target_url})")
    else:
        target_url = f"{MONOLITH_URL}/api/orders"
        print(f"🔀 Routing /api/orders → LEGACY Monolith ({target_url})")
    
    return _proxy_request(target_url)


@app.route("/api/orders/<order_id>", methods=["GET"])
def proxy_order_by_id(order_id):
    if get_flag("orders.use_new_service"):
        target_url = f"{ORDER_SERVICE_URL}/api/orders/{order_id}"
    else:
        target_url = f"{MONOLITH_URL}/api/orders/{order_id}"
    
    return _proxy_request(target_url)


# ==================== INVENTORY ROUTES (Always to monolith) ====================

@app.route("/api/inventory", methods=["GET"])
@app.route("/api/inventory/<product>", methods=["GET"])
def proxy_inventory(product=None):
    if product:
        target_url = f"{MONOLITH_URL}/api/inventory/{product}"
    else:
        target_url = f"{MONOLITH_URL}/api/inventory"
    print(f"🔀 Routing /api/inventory → LEGACY Monolith (not migrated)")
    return _proxy_request(target_url)


# ==================== PAYMENT ROUTES (Always to monolith) ====================

@app.route("/api/payments", methods=["POST"])
def proxy_payments():
    target_url = f"{MONOLITH_URL}/api/payments"
    print(f"🔀 Routing /api/payments → LEGACY Monolith (not migrated)")
    return _proxy_request(target_url)


# ==================== ADMIN ENDPOINTS ====================

@app.route("/admin/flags", methods=["GET"])
def get_flags():
    return jsonify(feature_flags)


@app.route("/admin/flags/<flag_name>", methods=["PUT"])
def toggle_flag(flag_name):
    data = request.json
    feature_flags[flag_name] = data.get("enabled", False)
    status = "ENABLED" if feature_flags[flag_name] else "DISABLED"
    print(f"⚡ Feature flag '{flag_name}' → {status}")
    return jsonify({"flag": flag_name, "enabled": feature_flags[flag_name]})


# ==================== PROXY HELPER ====================

def _proxy_request(target_url):
    """Forward the incoming request to the target URL."""
    try:
        if request.method == "GET":
            resp = requests.get(target_url, params=request.args, timeout=5)
        elif request.method == "POST":
            resp = requests.post(target_url, json=request.json, timeout=5)
        elif request.method == "PUT":
            resp = requests.put(target_url, json=request.json, timeout=5)
        else:
            resp = requests.request(request.method, target_url, timeout=5)

        return (resp.content, resp.status_code, resp.headers.items())
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Backend service unavailable", "target": target_url}), 503


if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════╗")
    print("║          STRANGLER FIG — Facade Router (Port 5000)      ║")
    print("╠══════════════════════════════════════════════════════════╣")
    print("║  Routing Rules:                                         ║")
    print("║  /api/orders    → New Service (flag ON) or Monolith     ║")
    print("║  /api/inventory → Legacy Monolith                       ║")
    print("║  /api/payments  → Legacy Monolith                       ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"\n  Feature Flags: {feature_flags}")
    app.run(port=5000, debug=True)
