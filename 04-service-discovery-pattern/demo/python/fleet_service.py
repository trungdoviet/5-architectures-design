"""
============================================================
SERVICE DISCOVERY PATTERN — Fleet Service
============================================================
Manages delivery vehicles and drivers.
Self-registers with the registry and sends periodic heartbeats.
Runs on port 8001.
"""

from flask import Flask, jsonify
import requests
import threading
import time
import atexit

app = Flask(__name__)

REGISTRY_URL = "http://localhost:7000"
SERVICE_NAME = "fleet"
INSTANCE_ID = "fleet-1"
HOST = "localhost"
PORT = 8001

vehicles = [
    {"id": "VH-001", "type": "Truck", "capacity": "10 tons", "status": "Available", "driver": "John Smith"},
    {"id": "VH-002", "type": "Van", "capacity": "2 tons", "status": "In Transit", "driver": "Jane Doe"},
    {"id": "VH-003", "type": "Truck", "capacity": "10 tons", "status": "Available", "driver": "Mike Johnson"},
    {"id": "VH-004", "type": "Motorcycle", "capacity": "50 kg", "status": "Available", "driver": "Sarah Lee"},
]


@app.route("/fleet/vehicles", methods=["GET"])
def list_vehicles():
    return jsonify({"vehicles": vehicles, "source": INSTANCE_ID})


@app.route("/fleet/available", methods=["GET"])
def available_vehicles():
    available = [v for v in vehicles if v["status"] == "Available"]
    return jsonify({"available_vehicles": available, "count": len(available)})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": SERVICE_NAME, "instance": INSTANCE_ID})


def register_with_registry():
    """Self-register with the service registry on startup."""
    try:
        requests.post(f"{REGISTRY_URL}/register", json={
            "instance_id": INSTANCE_ID,
            "service_name": SERVICE_NAME,
            "host": HOST,
            "port": PORT,
            "metadata": {"type": "fleet-management"},
        })
        print(f"  ✅ Registered with registry as '{INSTANCE_ID}'")
    except Exception as e:
        print(f"  ❌ Failed to register: {e}")


def heartbeat_loop():
    """Send periodic heartbeats to the registry."""
    while True:
        time.sleep(10)
        try:
            requests.put(f"{REGISTRY_URL}/heartbeat/{INSTANCE_ID}")
        except Exception:
            pass


def deregister():
    """Deregister from the registry on shutdown."""
    try:
        requests.delete(f"{REGISTRY_URL}/deregister/{INSTANCE_ID}")
    except Exception:
        pass


if __name__ == "__main__":
    register_with_registry()
    atexit.register(deregister)
    
    heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
    heartbeat_thread.start()
    
    print(f"🚛 Fleet Service starting on port {PORT}...")
    app.run(port=PORT, debug=False)
