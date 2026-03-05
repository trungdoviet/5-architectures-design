"""
============================================================
CIRCUIT BREAKER PATTERN — Booking Service
============================================================
Medical appointment booking service that uses a Circuit Breaker
to protect calls to the Payment Service.
Runs on port 6000.
"""

from flask import Flask, jsonify, request
import requests as http_client
import time
import threading

app = Flask(__name__)

PAYMENT_URL = "http://localhost:6001"


# =============================================
# Circuit Breaker Implementation
# =============================================

class CircuitBreaker:
    """
    Circuit Breaker with three states:
      CLOSED    → Normal operation, counting failures
      OPEN      → Rejecting all requests with fallback
      HALF_OPEN → Allowing one test request
    """
    
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"
    
    def __init__(self, name, failure_threshold=3, recovery_timeout=10):
        self.name = name
        self.state = self.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout  # seconds
        self.last_failure_time = None
        self.state_log = []
        self._lock = threading.Lock()
        self._log_transition("INITIALIZED", self.CLOSED)
    
    def allow_request(self):
        with self._lock:
            if self.state == self.CLOSED:
                return True
            elif self.state == self.OPEN:
                if self.last_failure_time and (time.time() - self.last_failure_time >= self.recovery_timeout):
                    self._transition(self.HALF_OPEN)
                    return True
                return False
            elif self.state == self.HALF_OPEN:
                return True
            return False
    
    def record_success(self):
        with self._lock:
            if self.state == self.HALF_OPEN:
                self._transition(self.CLOSED)
                self.failure_count = 0
            elif self.state == self.CLOSED:
                self.failure_count = 0
    
    def record_failure(self):
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == self.CLOSED:
                if self.failure_count >= self.failure_threshold:
                    self._transition(self.OPEN)
                else:
                    print(f"  ⚠️ [{self.name}] Failure {self.failure_count}/{self.failure_threshold}")
            elif self.state == self.HALF_OPEN:
                self._transition(self.OPEN)
    
    def _transition(self, new_state):
        old_state = self.state
        self.state = new_state
        self._log_transition(f"{old_state} → {new_state}", new_state)
        print(f"  🔄 [{self.name}] Circuit: {old_state} → {new_state}")
    
    def _log_transition(self, msg, state):
        self.state_log.append({
            "timestamp": time.strftime("%H:%M:%S"),
            "transition": msg,
            "state": state,
            "failures": self.failure_count,
        })
    
    def get_status(self):
        return {
            "name": self.name,
            "state": self.state,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
            "state_log": self.state_log,
        }


# Initialize circuit breaker
payment_circuit = CircuitBreaker(
    name="PaymentCircuit",
    failure_threshold=3,
    recovery_timeout=10,
)

appointment_counter = 0


# =============================================
# Booking Endpoints
# =============================================

@app.route("/appointments/book", methods=["POST"])
def book_appointment():
    global appointment_counter
    data = request.json
    appointment_counter += 1
    appointment_id = f"APT-{appointment_counter:04d}"
    
    result = {
        "appointment_id": appointment_id,
        "patient": data.get("patient", "Unknown"),
        "doctor": data.get("doctor", "Unknown"),
        "date": data.get("date", "TBD"),
        "fee": data.get("fee", 0),
    }
    
    # Process payment through circuit breaker
    if payment_circuit.allow_request():
        try:
            resp = http_client.post(f"{PAYMENT_URL}/payments/process", json={
                "appointment_id": appointment_id,
                "amount": data.get("fee", 0),
            }, timeout=5)
            
            if resp.status_code == 200:
                payment_circuit.record_success()
                payment_data = resp.json()
                result["payment_status"] = "PAID"
                result["payment_id"] = payment_data.get("payment_id")
                result["circuit_state"] = payment_circuit.state
            else:
                payment_circuit.record_failure()
                result["payment_status"] = "DEFERRED"
                result["fallback"] = "Payment will be retried when service recovers"
                result["circuit_state"] = payment_circuit.state
                
        except Exception as e:
            payment_circuit.record_failure()
            result["payment_status"] = "DEFERRED"
            result["fallback"] = f"Payment failed: {str(e)[:50]}. Will retry later."
            result["circuit_state"] = payment_circuit.state
    else:
        # Circuit OPEN — fast fail
        result["payment_status"] = "DEFERRED"
        result["fallback"] = "🔴 Circuit OPEN — payment skipped (fast fail)"
        result["circuit_state"] = payment_circuit.state
    
    return jsonify(result), 201


@app.route("/circuit/status", methods=["GET"])
def circuit_status():
    return jsonify(payment_circuit.get_status())


@app.route("/circuit/reset", methods=["POST"])
def reset_circuit():
    payment_circuit.state = CircuitBreaker.CLOSED
    payment_circuit.failure_count = 0
    return jsonify({"message": "Circuit reset to CLOSED", "status": payment_circuit.get_status()})


if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════╗")
    print("║    BOOKING SERVICE — with Circuit Breaker (Port 6000)   ║")
    print("╠══════════════════════════════════════════════════════════╣")
    print(f"║  Failure threshold:  {payment_circuit.failure_threshold} consecutive failures          ║")
    print(f"║  Recovery timeout:   {payment_circuit.recovery_timeout} seconds                        ║")
    print("╚══════════════════════════════════════════════════════════╝")
    app.run(port=6000, debug=True)
