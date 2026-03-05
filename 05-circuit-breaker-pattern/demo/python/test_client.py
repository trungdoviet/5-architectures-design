"""
============================================================
CIRCUIT BREAKER PATTERN — Test Client
============================================================
Demonstrates the full circuit breaker lifecycle:
  1. Normal operation (CLOSED)
  2. Failures trip the breaker (OPEN)
  3. Fallback responses
  4. Recovery (HALF-OPEN → CLOSED)
"""

import requests
import json
import time

BOOKING_URL = "http://localhost:6000"
PAYMENT_URL = "http://localhost:6001"


def print_section(title):
    print(f"\n{'━' * 60}")
    print(f"  {title}")
    print(f"{'━' * 60}")


def book_appointment(patient, doctor, fee):
    resp = requests.post(f"{BOOKING_URL}/appointments/book", json={
        "patient": patient,
        "doctor": doctor,
        "fee": fee,
        "date": "2024-02-15",
    })
    data = resp.json()
    status_icon = "✅" if data.get("payment_status") == "PAID" else "⚠️"
    print(f"\n  {status_icon} {data['appointment_id']} | {data['patient']} → {data['doctor']}")
    print(f"     Payment: {data['payment_status']} | Circuit: {data.get('circuit_state', '?')}")
    if "fallback" in data:
        print(f"     Fallback: {data['fallback']}")
    return data


def get_circuit_status():
    resp = requests.get(f"{BOOKING_URL}/circuit/status")
    data = resp.json()
    print(f"\n  🔌 Circuit State: {data['state']} | Failures: {data['failure_count']}/{data['failure_threshold']}")
    return data


def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   CIRCUIT BREAKER PATTERN — Test Client                 ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # ---- Phase 1: Normal operation ----
    print_section("PHASE 1: Normal Operation (Circuit CLOSED)")
    book_appointment("Alice Smith", "Dr. Johnson", 150.00)
    book_appointment("Bob Wilson", "Dr. Lee", 200.00)
    get_circuit_status()

    # ---- Phase 2: Kill payment service ----
    print_section("PHASE 2: Payment Service Goes DOWN")
    print("  Toggling payment service to unhealthy...")
    try:
        requests.post(f"{PAYMENT_URL}/admin/toggle")
        print("  ❌ Payment Service is now DOWN")
    except Exception:
        print("  ⚠️ Could not toggle payment service (may need manual toggle)")

    # ---- Phase 3: Failures accumulate ----
    print_section("PHASE 3: Failures Accumulate → Circuit OPENS")
    book_appointment("Charlie Brown", "Dr. Johnson", 175.00)  # Failure 1
    book_appointment("Diana Ross", "Dr. Lee", 250.00)         # Failure 2
    book_appointment("Eve Davis", "Dr. Smith", 300.00)         # Failure 3 → OPEN
    get_circuit_status()

    # ---- Phase 4: Circuit OPEN (fast fail) ----
    print_section("PHASE 4: Circuit OPEN — All Requests Fast-Fail")
    book_appointment("Frank Miller", "Dr. Johnson", 150.00)    # Fast fail
    book_appointment("Grace Lee", "Dr. Lee", 200.00)           # Fast fail
    print("\n  ⚡ Notice: No calls to Payment Service! Responses are instant.")
    get_circuit_status()

    # ---- Phase 5: Recovery ----
    print_section("PHASE 5: Payment Service Recovers")
    print("  Toggling payment service back to healthy...")
    try:
        requests.post(f"{PAYMENT_URL}/admin/toggle")
        print("  ✅ Payment Service is now HEALTHY")
    except Exception:
        print("  ⚠️ Could not toggle payment service")

    print(f"\n  Waiting for circuit recovery timeout (10 seconds)...")
    for i in range(10, 0, -1):
        print(f"  ⏱️ {i}s remaining...", end="\r")
        time.sleep(1)
    print("  ⏱️ Timeout elapsed!       ")

    # ---- Phase 6: HALF-OPEN test ----
    print_section("PHASE 6: HALF-OPEN → Test Request → CLOSED")
    book_appointment("Henry Zhang", "Dr. Johnson", 175.00)    # Test → Success → CLOSED
    get_circuit_status()

    # ---- Phase 7: Back to normal ----
    print_section("PHASE 7: Back to Normal Operation")
    book_appointment("Iris Wang", "Dr. Lee", 225.00)
    book_appointment("Jack Chen", "Dr. Smith", 195.00)
    get_circuit_status()

    # ---- State log ----
    print_section("CIRCUIT BREAKER STATE LOG")
    status = requests.get(f"{BOOKING_URL}/circuit/status").json()
    for entry in status.get("state_log", []):
        print(f"  [{entry['timestamp']}] {entry['transition']} (failures: {entry['failures']})")

    print("\n✅ Demo complete!")
    print("   The Circuit Breaker prevented cascading failures and self-healed!")


if __name__ == "__main__":
    main()
