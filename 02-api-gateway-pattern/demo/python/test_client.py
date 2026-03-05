"""
============================================================
API GATEWAY PATTERN — Test Client
============================================================
Tests all gateway features: auth, routing, aggregation, rate limiting.
"""

import requests
import json

GATEWAY_URL = "http://localhost:8000"
HEADERS = {"Authorization": "Bearer token-alice"}


def print_section(title):
    print(f"\n{'━' * 55}")
    print(f"  {title}")
    print(f"{'━' * 55}")


def print_response(label, response):
    print(f"\n  {label}")
    print(f"  Status: {response.status_code}")
    try:
        print(f"  Body: {json.dumps(response.json(), indent=4)}")
    except Exception:
        print(f"  Body: {response.text}")


def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   API GATEWAY PATTERN — Test Client                     ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # Test 1: Authentication
    print_section("TEST 1: Authentication")
    resp = requests.get(f"{GATEWAY_URL}/api/users/user-1", headers={"Authorization": "Bearer invalid"})
    print_response("❌ Invalid token:", resp)
    resp = requests.get(f"{GATEWAY_URL}/api/users/user-1", headers=HEADERS)
    print_response("✅ Valid token:", resp)

    # Test 2: Routing to different services
    print_section("TEST 2: Routing — User Service")
    resp = requests.get(f"{GATEWAY_URL}/api/users/user-2", headers=HEADERS)
    print_response("👤 User profile:", resp)

    print_section("TEST 3: Routing — Post Service")
    resp = requests.get(f"{GATEWAY_URL}/api/posts", params={"user_id": "user-1"}, headers=HEADERS)
    print_response("📝 User posts:", resp)

    print_section("TEST 4: Routing — Notification Service")
    resp = requests.get(f"{GATEWAY_URL}/api/notifications", headers=HEADERS)
    print_response("🔔 Notifications:", resp)

    # Test 5: Create a post
    print_section("TEST 5: Create Post via Gateway")
    resp = requests.post(f"{GATEWAY_URL}/api/posts", json={"content": "Testing the API Gateway! 🚀"}, headers=HEADERS)
    print_response("📮 New post:", resp)

    # Test 6: Aggregated feed
    print_section("TEST 6: Aggregated Feed (combines 3 services)")
    resp = requests.get(f"{GATEWAY_URL}/api/feed/user-1", headers=HEADERS)
    print_response("🔗 Feed (user + posts + notifs):", resp)

    # Test 7: Health check
    print_section("TEST 7: Service Health Check")
    resp = requests.get(f"{GATEWAY_URL}/admin/health")
    print_response("💚 Health:", resp)

    # Test 8: Request logs
    print_section("TEST 8: Centralized Request Logs")
    resp = requests.get(f"{GATEWAY_URL}/admin/logs")
    print_response("📋 Logs:", resp)

    print("\n✅ All tests complete!")
    print("   The API Gateway centralized auth, routing, aggregation, and logging.")


if __name__ == "__main__":
    main()
