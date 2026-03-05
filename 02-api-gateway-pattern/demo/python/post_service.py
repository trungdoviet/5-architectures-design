"""
============================================================
API GATEWAY PATTERN — Post Service
============================================================
Manages posts and likes. Runs on port 8002.
"""

from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

posts = {
    "post-1": {"id": "post-1", "user_id": "user-1", "content": "Just deployed our new microservices architecture! 🚀", "likes": 42, "timestamp": "2024-01-15T10:30:00"},
    "post-2": {"id": "post-2", "user_id": "user-1", "content": "API Gateway Pattern is a game changer.", "likes": 28, "timestamp": "2024-01-16T14:00:00"},
    "post-3": {"id": "post-3", "user_id": "user-2", "content": "Designed a beautiful new dashboard today 🎨", "likes": 55, "timestamp": "2024-01-16T09:00:00"},
    "post-4": {"id": "post-4", "user_id": "user-3", "content": "Training a new ML model — 98% accuracy!", "likes": 120, "timestamp": "2024-01-17T11:00:00"},
}
post_counter = 4


@app.route("/posts", methods=["GET"])
def list_posts():
    user_id = request.args.get("user_id")
    if user_id:
        filtered = [p for p in posts.values() if p["user_id"] == user_id]
        return jsonify({"posts": filtered, "source": "POST_SERVICE"})
    return jsonify({"posts": list(posts.values()), "source": "POST_SERVICE"})


@app.route("/posts", methods=["POST"])
def create_post():
    global post_counter
    data = request.json
    post_counter += 1
    post_id = f"post-{post_counter}"
    post = {
        "id": post_id,
        "user_id": data["user_id"],
        "content": data["content"],
        "likes": 0,
        "timestamp": datetime.now().isoformat(),
    }
    posts[post_id] = post
    return jsonify(post), 201


@app.route("/posts/<post_id>/like", methods=["POST"])
def like_post(post_id):
    post = posts.get(post_id)
    if post:
        post["likes"] += 1
        return jsonify(post)
    return jsonify({"error": "Post not found"}), 404


if __name__ == "__main__":
    print("📝 Post Service starting on port 8002...")
    app.run(port=8002, debug=True)
