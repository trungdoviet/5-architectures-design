"""
============================================================
API GATEWAY PATTERN — User Service
============================================================
Manages user profiles. Runs on port 8001.
"""

from flask import Flask, jsonify

app = Flask(__name__)

users = {
    "user-1": {"id": "user-1", "username": "alice", "email": "alice@example.com", "bio": "Software Engineer", "followers": 1500, "following": 300},
    "user-2": {"id": "user-2", "username": "bob", "email": "bob@example.com", "bio": "Product Designer", "followers": 800, "following": 200},
    "user-3": {"id": "user-3", "username": "charlie", "email": "charlie@example.com", "bio": "Data Scientist", "followers": 2000, "following": 150},
}


@app.route("/users", methods=["GET"])
def list_users():
    return jsonify({"users": list(users.values()), "source": "USER_SERVICE"})


@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    user = users.get(user_id)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404


if __name__ == "__main__":
    print("👤 User Service starting on port 8001...")
    app.run(port=8001, debug=True)
