"""
============================================================
CIRCUIT BREAKER PATTERN — Payment Service (Unreliable)
============================================================
Simulates an unreliable payment service that can be toggled
between healthy and unhealthy states.
Runs on port 6001.
"""

from flask import Flask, jsonify, request
import random

app = Flask(__name__)

# Service state
is_healthy = True
failure_rate = 0.0  # 0.0 = always succeed, 1.0 = always fail


@app.route("/payments/process", methods=["POST"])
def process_payment():
    if not is_healthy or random.random() < failure_rate:
        return jsonify({"error": "Payment Service Error", "message": "Service is currently unavailable"}), 503
    
    data = request.json
    return jsonify({
        "payment_id": f"PAY-{random.randint(1000, 9999)}",
        "appointment_id": data.get("appointment_id"),
        "amount": data.get("amount"),
        "status": "COMPLETED",
        "message": f"Payment of ${data.get('amount', 0):.2f} processed successfully",
    })


@app.route("/health", methods=["GET"])
def health():
    if is_healthy:
        return jsonify({"status": "healthy"})
    return jsonify({"status": "unhealthy"}), 503


@app.route("/admin/toggle", methods=["POST"])
def toggle_health():
    global is_healthy
    is_healthy = not is_healthy
    status = "HEALTHY" if is_healthy else "DOWN"
    print(f"  {'✅' if is_healthy else '❌'} Payment Service is now {status}")
    return jsonify({"status": status, "is_healthy": is_healthy})


@app.route("/admin/set-failure-rate", methods=["POST"])
def set_failure_rate():
    global failure_rate
    data = request.json
    failure_rate = data.get("rate", 0.0)
    print(f"  ⚙️ Failure rate set to {failure_rate*100:.0f}%")
    return jsonify({"failure_rate": failure_rate})


if __name__ == "__main__":
    print("💳 Payment Service starting on port 6001...")
    print("   Toggle health: POST /admin/toggle")
    print("   Set failure rate: POST /admin/set-failure-rate")
    app.run(port=6001, debug=True)
