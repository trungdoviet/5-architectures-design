"""
============================================================
SERVICE DISCOVERY PATTERN — Warehouse Service
============================================================
Manages warehouse inventory. Supports MULTIPLE INSTANCES
to demonstrate load balancing via service discovery.

Usage:
  python warehouse_service.py 8003   # Instance 1
  python warehouse_service.py 8004   # Instance 2
"""

from flask import Flask, jsonify
import requests
import threading
import time
import sys
import atexit

app = Flask(__name__)

REGISTRY_URL = "http://localhost:7000"
SERVICE_NAME = "warehouse"
HOST = "localhost"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8003
INSTANCE_ID = f"warehouse-{PORT}"

# Different inventory per instance to show we're hitting different ones
inventory = {
    8003: {
        "name": "North Warehouse",
        "items": {"Electronics": 500, "Clothing": 1200, "Furniture": 80},
    },
    8004: {
        "name": "South Warehouse",
        "items": {"Electronics": 300, "Food": 5000, "Automotive": 150},
    },
}

warehouse_data = inventory.get(PORT, {"name": f"Warehouse-{PORT}", "items": {}})


@app.route("/warehouse/inventory", methods=["GET"])
def get_inventory():
    return jsonify({
        "warehouse": warehouse_data["name"],
        "instance_id": INSTANCE_ID,
        "inventory": warehouse_data["items"],
        "port": PORT,
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "instance": INSTANCE_ID})


def register_with_registry():
    try:
        requests.post(f"{REGISTRY_URL}/register", json={
            "instance_id": INSTANCE_ID,
            "service_name": SERVICE_NAME,
            "host": HOST,
            "port": PORT,
            "metadata": {"warehouse_name": warehouse_data["name"]},
        })
        print(f"  ✅ Registered with registry as '{INSTANCE_ID}'")
    except Exception as e:
        print(f"  ❌ Failed to register: {e}")


def heartbeat_loop():
    while True:
        time.sleep(10)
        try:
            requests.put(f"{REGISTRY_URL}/heartbeat/{INSTANCE_ID}")
        except Exception:
            pass


def deregister():
    try:
        requests.delete(f"{REGISTRY_URL}/deregister/{INSTANCE_ID}")
    except Exception:
        pass


if __name__ == "__main__":
    register_with_registry()
    atexit.register(deregister)
    
    heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
    heartbeat_thread.start()
    
    print(f"🏭 Warehouse Service ({warehouse_data['name']}) starting on port {PORT}...")
    app.run(port=PORT, debug=False)
