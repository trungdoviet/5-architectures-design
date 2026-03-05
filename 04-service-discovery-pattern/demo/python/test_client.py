"""
============================================================
SERVICE DISCOVERY PATTERN — Test Client
============================================================
Demonstrates service discovery, load balancing, and failure handling.
"""

import requests
import json
import random
import time

REGISTRY_URL = "http://localhost:7000"


def print_section(title):
    print(f"\n{'━' * 60}")
    print(f"  {title}")
    print(f"{'━' * 60}")


def discover_and_call(service_name, endpoint):
    """Discover a service and call one of its instances."""
    resp = requests.get(f"{REGISTRY_URL}/discover/{service_name}")
    data = resp.json()
    instances = data["instances"]
    
    if not instances:
        print(f"  ❌ No instances of '{service_name}' available!")
        return None
    
    # Client-side load balancing: random selection
    instance = random.choice(instances)
    url = f"http://{instance['host']}:{instance['port']}{endpoint}"
    print(f"  🎯 Discovered {len(instances)} instance(s) of '{service_name}'")
    print(f"     Selected: {instance['instance_id']} @ {instance['host']}:{instance['port']}")
    
    try:
        resp = requests.get(url, timeout=5)
        return resp.json()
    except Exception as e:
        print(f"  ❌ Call failed: {e}")
        return None


def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   SERVICE DISCOVERY PATTERN — Test Client               ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # Test 1: View registry
    print_section("TEST 1: View Service Registry")
    resp = requests.get(f"{REGISTRY_URL}/registry")
    data = resp.json()
    print(f"  Total registered instances: {data['total_instances']}")
    for svc in data["services"]:
        print(f"    • {svc['instance_id']} ({svc['service_name']}) → {svc['host']}:{svc['port']} [{svc['status']}]")

    # Test 2: Discover fleet service
    print_section("TEST 2: Discover & Call Fleet Service")
    result = discover_and_call("fleet", "/fleet/vehicles")
    if result:
        print(f"\n  Vehicles found: {len(result.get('vehicles', []))}")
        for v in result.get("vehicles", []):
            print(f"    🚛 {v['id']} - {v['type']} - {v['status']} ({v['driver']})")

    # Test 3: Discover warehouse (multiple instances)
    print_section("TEST 3: Discover Warehouse (Multiple Instances)")
    for i in range(3):
        print(f"\n  --- Request #{i + 1} ---")
        result = discover_and_call("warehouse", "/warehouse/inventory")
        if result:
            print(f"  📦 Warehouse: {result['warehouse']} (instance: {result['instance_id']})")
            print(f"     Inventory: {result['inventory']}")

    # Test 4: Discover non-existent service
    print_section("TEST 4: Discover Non-Existent Service")
    resp = requests.get(f"{REGISTRY_URL}/discover/non-existent")
    data = resp.json()
    print(f"  Service: {data['service']}")
    print(f"  Instances found: {data['count']}")
    print(f"  Result: {'❌ Service not available' if data['count'] == 0 else '✅ Found'}")

    # Test 5: Health-based discovery
    print_section("TEST 5: Registry Health Status")
    resp = requests.get(f"{REGISTRY_URL}/registry")
    data = resp.json()
    healthy = sum(1 for s in data["services"] if s["status"] == "HEALTHY")
    unhealthy = sum(1 for s in data["services"] if s["status"] == "UNHEALTHY")
    print(f"  Healthy instances:   {healthy}")
    print(f"  Unhealthy instances: {unhealthy}")

    print("\n✅ All tests complete!")
    print("   Service Discovery enabled dynamic, location-transparent communication.")


if __name__ == "__main__":
    main()
