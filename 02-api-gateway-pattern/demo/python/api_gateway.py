"""
============================================================
API GATEWAY PATTERN — API Gateway (Centralized Entry Point)
============================================================

The API Gateway provides:
  ✅ Single entry point (port 8000)
  ✅ JWT-like authentication
  ✅ Rate limiting
  ✅ Request routing
  ✅ Request aggregation
  ✅ Centralized logging

Routes:
  /api/users/{id}         → User Service (8001)
  /api/posts              → Post Service (8002)
  /api/notifications      → Notification Service (8003)
  /api/feed/{userId}      → Aggregated (User + Post + Notification)
"""

from flask import Flask, jsonify, request
import requests as http_client
from datetime import datetime
from functools import wraps
import time

app = Flask(__name__)

# Service registry
SERVICES = {
    "user": "http://localhost:8001",
    "post": "http://localhost:8002",
    "notification": "http://localhost:8003",
}

# Valid tokens (in production, use JWT verification)
VALID_TOKENS = {
    "token-alice": "user-1",
    "token-bob": "user-2",
    "token-charlie": "user-3",
}

# Rate limiting storage
rate_limits = {}
MAX_REQUESTS_PER_MINUTE = 20

# Request log
request_log = []


# ==================== CROSS-CUTTING CONCERNS ====================

def log_request(method, path, user_id, status_code):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "method": method,
        "path": path,
        "user_id": user_id,
        "status_code": status_code,
    }
    request_log.append(entry)
    print(f"  📝 [{entry['timestamp']}] {method} {path} → {status_code} (user: {user_id})")


def authenticate():
    """Extract and validate the authorization token."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token not in VALID_TOKENS:
        return None, "Invalid token"
    return VALID_TOKENS[token], None


def check_rate_limit(user_id):
    """Check if the user has exceeded the rate limit."""
    now = time.time()
    if user_id not in rate_limits:
        rate_limits[user_id] = []
    
    # Remove old entries (older than 60 seconds)
    rate_limits[user_id] = [t for t in rate_limits[user_id] if now - t < 60]
    
    if len(rate_limits[user_id]) >= MAX_REQUESTS_PER_MINUTE:
        return False
    
    rate_limits[user_id].append(now)
    return True


def require_auth(f):
    """Decorator for authentication + rate limiting."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id, error = authenticate()
        if error:
            log_request(request.method, request.path, "anonymous", 401)
            return jsonify({"error": "Unauthorized", "message": error}), 401
        
        if not check_rate_limit(user_id):
            log_request(request.method, request.path, user_id, 429)
            return jsonify({"error": "Rate limit exceeded", "retry_after": 60}), 429
        
        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated


# ==================== GATEWAY ROUTES ====================

@app.route("/api/users/<user_id>", methods=["GET"])
@require_auth
def get_user(user_id):
    """Route to User Service."""
    try:
        resp = http_client.get(f"{SERVICES['user']}/users/{user_id}", timeout=5)
        log_request("GET", f"/api/users/{user_id}", request.user_id, resp.status_code)
        return (resp.content, resp.status_code, {"Content-Type": "application/json"})
    except http_client.exceptions.ConnectionError:
        log_request("GET", f"/api/users/{user_id}", request.user_id, 503)
        return jsonify({"error": "User Service unavailable"}), 503


@app.route("/api/posts", methods=["GET", "POST"])
@require_auth
def handle_posts():
    """Route to Post Service."""
    try:
        if request.method == "GET":
            resp = http_client.get(f"{SERVICES['post']}/posts", params=request.args, timeout=5)
        else:
            data = request.json
            data["user_id"] = request.user_id
            resp = http_client.post(f"{SERVICES['post']}/posts", json=data, timeout=5)
        
        log_request(request.method, "/api/posts", request.user_id, resp.status_code)
        return (resp.content, resp.status_code, {"Content-Type": "application/json"})
    except http_client.exceptions.ConnectionError:
        log_request(request.method, "/api/posts", request.user_id, 503)
        return jsonify({"error": "Post Service unavailable"}), 503


@app.route("/api/notifications", methods=["GET"])
@require_auth
def get_notifications():
    """Route to Notification Service."""
    try:
        resp = http_client.get(f"{SERVICES['notification']}/notifications/{request.user_id}", timeout=5)
        log_request("GET", "/api/notifications", request.user_id, resp.status_code)
        return (resp.content, resp.status_code, {"Content-Type": "application/json"})
    except http_client.exceptions.ConnectionError:
        log_request("GET", "/api/notifications", request.user_id, 503)
        return jsonify({"error": "Notification Service unavailable"}), 503


@app.route("/api/feed/<user_id>", methods=["GET"])
@require_auth
def get_user_feed(user_id):
    """
    AGGREGATION ENDPOINT
    Combines data from User + Post + Notification services into a single response.
    This is a key feature of the API Gateway Pattern.
    """
    feed = {"aggregated_by": "API_GATEWAY", "timestamp": datetime.now().isoformat()}
    
    # Fetch user profile
    try:
        resp = http_client.get(f"{SERVICES['user']}/users/{user_id}", timeout=5)
        feed["user"] = resp.json()
    except Exception:
        feed["user"] = {"error": "User Service unavailable"}
    
    # Fetch user posts
    try:
        resp = http_client.get(f"{SERVICES['post']}/posts", params={"user_id": user_id}, timeout=5)
        feed["posts"] = resp.json()
    except Exception:
        feed["posts"] = {"error": "Post Service unavailable"}
    
    # Fetch notifications
    try:
        resp = http_client.get(f"{SERVICES['notification']}/notifications/{user_id}", timeout=5)
        feed["notifications"] = resp.json()
    except Exception:
        feed["notifications"] = {"error": "Notification Service unavailable"}
    
    log_request("GET", f"/api/feed/{user_id}", request.user_id, 200)
    return jsonify(feed)


# ==================== ADMIN ENDPOINTS ====================

@app.route("/admin/logs", methods=["GET"])
def get_request_log():
    return jsonify({"logs": request_log[-50:], "total": len(request_log)})


@app.route("/admin/health", methods=["GET"])
def health_check():
    health = {}
    for name, url in SERVICES.items():
        try:
            http_client.get(url, timeout=2)
            health[name] = "UP"
        except Exception:
            health[name] = "DOWN"
    return jsonify({"gateway": "UP", "services": health})


if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         API GATEWAY — Social Network (Port 8000)        ║")
    print("╠══════════════════════════════════════════════════════════╣")
    print("║  Routes:                                                ║")
    print("║  /api/users/{id}     → User Service     (8001)          ║")
    print("║  /api/posts          → Post Service     (8002)          ║")
    print("║  /api/notifications  → Notification Svc (8003)          ║")
    print("║  /api/feed/{userId}  → Aggregated Response              ║")
    print("╚══════════════════════════════════════════════════════════╝")
    app.run(port=8000, debug=True)
