"""
============================================================
STRANGLER FIG PATTERN — Legacy Monolith (E-Commerce)
============================================================

This is the legacy monolith that handles ALL operations:
- Orders, Inventory, Payments

It runs as a Flask server on port 5001.
"""

from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# In-memory data stores
orders = {}
inventory = {
    "Laptop": {"product": "Laptop", "stock": 50, "price": 999.99},
    "Phone": {"product": "Phone", "stock": 100, "price": 699.99},
    "Tablet": {"product": "Tablet", "stock": 30, "price": 499.99},
}
order_counter = 0


# ==================== ORDER ENDPOINTS (Will be migrated) ====================

@app.route("/api/orders", methods=["POST"])
def create_order():
    global order_counter
    data = request.json
    order_counter += 1
    order_id = f"MONO-{order_counter}"
    
    order = {
        "id": order_id,
        "product": data["product"],
        "quantity": data["quantity"],
        "price": data["price"],
        "status": "CONFIRMED",
        "processed_by": "LEGACY_MONOLITH",
        "timestamp": datetime.now().isoformat(),
    }
    
    # Deduct inventory
    product = data["product"]
    if product in inventory:
        inventory[product]["stock"] -= data["quantity"]
    
    orders[order_id] = order
    return jsonify(order), 201


@app.route("/api/orders", methods=["GET"])
def list_orders():
    return jsonify({"orders": list(orders.values()), "source": "LEGACY_MONOLITH"})


@app.route("/api/orders/<order_id>", methods=["GET"])
def get_order(order_id):
    order = orders.get(order_id)
    if order:
        return jsonify(order)
    return jsonify({"error": "Order not found"}), 404


# ==================== INVENTORY ENDPOINTS (Stays in monolith) ====================

@app.route("/api/inventory", methods=["GET"])
def list_inventory():
    return jsonify({
        "inventory": list(inventory.values()),
        "source": "LEGACY_MONOLITH"
    })


@app.route("/api/inventory/<product>", methods=["GET"])
def check_stock(product):
    item = inventory.get(product)
    if item:
        return jsonify(item)
    return jsonify({"error": "Product not found"}), 404


# ==================== PAYMENT ENDPOINTS (Stays in monolith) ====================

@app.route("/api/payments", methods=["POST"])
def process_payment():
    data = request.json
    payment = {
        "payment_id": f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "order_id": data["order_id"],
        "amount": data["amount"],
        "status": "COMPLETED",
        "processed_by": "LEGACY_MONOLITH",
        "timestamp": datetime.now().isoformat(),
    }
    return jsonify(payment), 201


if __name__ == "__main__":
    print("🏢 Legacy Monolith starting on port 5001...")
    print("   Handles: Orders, Inventory, Payments")
    app.run(port=5001, debug=True)
