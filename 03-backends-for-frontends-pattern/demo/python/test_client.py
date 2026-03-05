"""
============================================================
BFF PATTERN — Test Client (Compares Web vs Mobile responses)
============================================================
"""

import requests
import json
import sys

WEB_BFF_URL = "http://localhost:9002"
MOBILE_BFF_URL = "http://localhost:9003"


def print_section(title):
    print(f"\n{'━' * 60}")
    print(f"  {title}")
    print(f"{'━' * 60}")


def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   BFF PATTERN — Web vs Mobile Response Comparison       ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # ---- Web BFF ----
    print_section("WEB BFF — Rich Dashboard Response")
    try:
        resp = requests.get(f"{WEB_BFF_URL}/web/dashboard")
        web_data = resp.json()
        web_size = len(json.dumps(web_data))
        print(json.dumps(web_data, indent=2))
        print(f"\n  📊 Response size: {web_size} bytes")
        print(f"  📊 Transactions returned: {len(web_data.get('transaction_history', []))}")
        print(f"  📊 Includes analytics: {bool(web_data.get('analytics'))}")
    except requests.exceptions.ConnectionError:
        print("  ❌ Web BFF not running on port 9002")
        web_size = 0

    # ---- Mobile BFF ----
    print_section("MOBILE BFF — Compact App Response")
    try:
        resp = requests.get(f"{MOBILE_BFF_URL}/mobile/dashboard")
        mobile_data = resp.json()
        mobile_size = len(json.dumps(mobile_data))
        print(json.dumps(mobile_data, indent=2))
        print(f"\n  📱 Response size: {mobile_size} bytes")
        print(f"  📱 Transactions returned: {len(mobile_data.get('recent_transactions', []))}")
        print(f"  📱 Has push notifications: {bool(mobile_data.get('mobile_features', {}).get('push_notification_token'))}")
    except requests.exceptions.ConnectionError:
        print("  ❌ Mobile BFF not running on port 9003")
        mobile_size = 0

    # ---- Comparison ----
    if web_size > 0 and mobile_size > 0:
        print_section("COMPARISON — Web BFF vs Mobile BFF")
        reduction = (1 - mobile_size / web_size) * 100
        print(f"  ┌───────────────────┬──────────────────┬──────────────────┐")
        print(f"  │ Metric            │ Web BFF          │ Mobile BFF       │")
        print(f"  ├───────────────────┼──────────────────┼──────────────────┤")
        print(f"  │ Response size     │ {web_size:>10} bytes │ {mobile_size:>10} bytes │")
        print(f"  │ Transactions      │ All (10)         │ Last 5           │")
        print(f"  │ Analytics         │ ✅ Full charts   │ ❌ None          │")
        print(f"  │ Account details   │ ✅ Full details  │ ✅ Name + Balance│")
        print(f"  │ Special features  │ CSV Export,Search│ Push, Biometric  │")
        print(f"  └───────────────────┴──────────────────┴──────────────────┘")
        print(f"\n  📉 Mobile response is {reduction:.0f}% smaller than web response!")

    print("\n✅ Demo complete! The BFF Pattern provides platform-optimized APIs.")


if __name__ == "__main__":
    main()
