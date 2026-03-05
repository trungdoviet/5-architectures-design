"""
============================================================
STRANGLER FIG PATTERN — Test Client
============================================================

Tests the full migration flow through the Facade Router:
1. Create orders (routed to new service when flag is ON)
2. Check inventory (always monolith)
3. Process payments (always monolith)
4. Toggle feature flag to demonstrate rollback
"""

import requests
import json

FACADE_URL = "http://localhost:5000"


def print_section(title):
    print(f"\n{'━' * 55}")
    print(f"  {title}")
    print(f"{'━' * 55}")


def print_response(label, response):
    print(f"\n  {label}")
    print(f"  Status: {response.status_code}")
    print(f"  Body: {json.dumps(response.json(), indent=4)}")


def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   STRANGLER FIG PATTERN — Test Client                   ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # ---- Test 1: Create order (goes to new service by default) ----
    print_section("TEST 1: Create Order (via Facade)")
    resp = requests.post(f"{FACADE_URL}/api/orders", json={
        "product": "Laptop",
        "quantity": 2,
        "price": 999.99,
    })
    print_response("📦 Order created:", resp)
    order_data = resp.json()

    # ---- Test 2: List orders ----
    print_section("TEST 2: List Orders")
    resp = requests.get(f"{FACADE_URL}/api/orders")
    print_response("📋 Orders list:", resp)

    # ---- Test 3: Check inventory (always monolith) ----
    print_section("TEST 3: Check Inventory (always via Monolith)")
    resp = requests.get(f"{FACADE_URL}/api/inventory/Laptop")
    print_response("📦 Laptop stock:", resp)

    # ---- Test 4: Process payment (always monolith) ----
    print_section("TEST 4: Process Payment (always via Monolith)")
    resp = requests.post(f"{FACADE_URL}/api/payments", json={
        "order_id": order_data.get("id", "SVC-1"),
        "amount": 1999.98,
    })
    print_response("💳 Payment result:", resp)

    # ---- Test 5: Toggle feature flag (rollback) ----
    print_section("TEST 5: Rollback — Disable new Order Service")
    resp = requests.put(f"{FACADE_URL}/admin/flags/orders.use_new_service", json={
        "enabled": False,
    })
    print_response("⚡ Flag toggled:", resp)

    # ---- Test 6: Create order again (should go to monolith now) ----
    print_section("TEST 6: Create Order After Rollback")
    resp = requests.post(f"{FACADE_URL}/api/orders", json={
        "product": "Phone",
        "quantity": 1,
        "price": 699.99,
    })
    print_response("📦 Order created (should be LEGACY):", resp)

    # ---- Test 7: Re-enable new service ----
    print_section("TEST 7: Re-enable New Order Service")
    resp = requests.put(f"{FACADE_URL}/admin/flags/orders.use_new_service", json={
        "enabled": True,
    })
    print_response("⚡ Flag toggled:", resp)

    resp = requests.post(f"{FACADE_URL}/api/orders", json={
        "product": "Tablet",
        "quantity": 3,
        "price": 499.99,
    })
    print_response("📦 Order created (should be NEW):", resp)

    print("\n✅ All tests complete!")
    print("   Notice how the 'processed_by' field changes based on the feature flag.")
    print("   This is the Strangler Fig Pattern in action!")


if __name__ == "__main__":
    main()
