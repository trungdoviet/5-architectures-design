"""
============================================================
SERVICE DISCOVERY PATTERN — Service Registry
============================================================

Central registry where services register, send heartbeats,
and discover other services. Runs on port 7000.

Endpoints:
  POST   /register        — Register a service instance
  PUT    /heartbeat/{id}   — Send heartbeat
  GET    /discover/{name}  — Find instances of a service
  GET    /registry         — View all registered services
  DELETE /deregister/{id}  — Remove a service
"""

from flask import Flask, jsonify, request
import time
import threading

app = Flask(__name__)

# Registry: instance_id → instance info
registry = {}
HEARTBEAT_TIMEOUT = 15  # seconds


# ==================== REGISTRATION ====================

@app.route("/register", methods=["POST"])
def register_service():
    data = request.json
    instance_id = data["instance_id"]
    registry[instance_id] = {
        "instance_id": instance_id,
        "service_name": data["service_name"],
        "host": data["host"],
        "port": data["port"],
        "status": "HEALTHY",
        "last_heartbeat": time.time(),
        "registered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "metadata": data.get("metadata", {}),
    }
    print(f"  📋 Registered: {instance_id} ({data['service_name']} @ {data['host']}:{data['port']})")
    return jsonify({"status": "registered", "instance_id": instance_id}), 201


# ==================== HEARTBEAT ====================

@app.route("/heartbeat/<instance_id>", methods=["PUT"])
def heartbeat(instance_id):
    if instance_id in registry:
        registry[instance_id]["last_heartbeat"] = time.time()
        registry[instance_id]["status"] = "HEALTHY"
        return jsonify({"status": "ok"})
    return jsonify({"error": "Instance not found"}), 404


# ==================== DISCOVERY ====================

@app.route("/discover/<service_name>", methods=["GET"])
def discover(service_name):
    instances = [
        inst for inst in registry.values()
        if inst["service_name"] == service_name and inst["status"] == "HEALTHY"
    ]
    return jsonify({
        "service": service_name,
        "instances": instances,
        "count": len(instances),
    })


# ==================== REGISTRY VIEW ====================

@app.route("/registry", methods=["GET"])
def view_registry():
    return jsonify({
        "services": list(registry.values()),
        "total_instances": len(registry),
    })


# ==================== DEREGISTRATION ====================

@app.route("/deregister/<instance_id>", methods=["DELETE"])
def deregister(instance_id):
    if instance_id in registry:
        del registry[instance_id]
        print(f"  📋 Deregistered: {instance_id}")
        return jsonify({"status": "deregistered"})
    return jsonify({"error": "Not found"}), 404


# ==================== HEALTH CHECK THREAD ====================

def health_check_loop():
    """Background thread that checks for dead instances."""
    while True:
        time.sleep(5)
        now = time.time()
        for instance_id, info in list(registry.items()):
            if now - info["last_heartbeat"] > HEARTBEAT_TIMEOUT:
                if info["status"] == "HEALTHY":
                    info["status"] = "UNHEALTHY"
                    print(f"  ⚠️ {instance_id} marked UNHEALTHY (no heartbeat for {HEARTBEAT_TIMEOUT}s)")


if __name__ == "__main__":
    # Start health check in background
    health_thread = threading.Thread(target=health_check_loop, daemon=True)
    health_thread.start()
    
    print("╔══════════════════════════════════════════════════════════╗")
    print("║       SERVICE REGISTRY — Logistics System (Port 7000)   ║")
    print("╚══════════════════════════════════════════════════════════╝")
    app.run(port=7000, debug=False)
