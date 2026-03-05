"""
============================================================
STRANGLER FIG PATTERN — New Order Service (Microservice)
============================================================

This is the NEW microservice that replaces the order module
from the monolith. It runs independently on port 5002.

In a real system, this would:
- Have its own database
- Communicate with other services via API/messaging
- Be independently deployable
"""

from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# Independent data store (own database in production)
orders = {}
order_counter = 0


@app.route("/api/orders", methods=["POST"])
def create_order():
    global order_counter
    data = request.json
    order_counter += 1
    order_id = f"SVC-{order_counter}"
    
    order = {
        "id": order_id,
        "product": data["product"],
        "quantity": data["quantity"],
        "price": data["price"],
        "status": "CONFIRMED",
        "processed_by": "NEW_ORDER_SERVICE",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "tracking_enabled": True,
            "real_time_updates": True,
            "async_processing": True,
        }
    }
    
    orders[order_id] = order
    print(f"✅ New Order Service processed order: {order_id}")
    return jsonify(order), 201


@app.route("/api/orders", methods=["GET"])
def list_orders():
    return jsonify({
        "orders": list(orders.values()),
        "source": "NEW_ORDER_SERVICE",
        "total": len(orders),
    })


@app.route("/api/orders/<order_id>", methods=["GET"])
def get_order(order_id):
    order = orders.get(order_id)
    if order:
        return jsonify(order)
    return jsonify({"error": "Order not found"}), 404


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "service": "order-service",
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
    })


if __name__ == "__main__":
    print("🚀 New Order Service starting on port 5002...")
    print("   This microservice replaces the Order module from the monolith")
    app.run(port=5002, debug=True)
