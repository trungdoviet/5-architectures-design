"""
============================================================
API GATEWAY PATTERN — Notification Service
============================================================
Manages user notifications. Runs on port 8003.
"""

from flask import Flask, jsonify

app = Flask(__name__)

notifications = {
    "user-1": [
        {"id": "notif-1", "user_id": "user-1", "message": "bob liked your post", "type": "LIKE", "read": False},
        {"id": "notif-2", "user_id": "user-1", "message": "charlie followed you", "type": "FOLLOW", "read": False},
    ],
    "user-2": [
        {"id": "notif-3", "user_id": "user-2", "message": "alice mentioned you", "type": "MENTION", "read": False},
    ],
    "user-3": [],
}


@app.route("/notifications/<user_id>", methods=["GET"])
def get_notifications(user_id):
    notifs = notifications.get(user_id, [])
    unread = len([n for n in notifs if not n["read"]])
    return jsonify({
        "notifications": notifs,
        "unread_count": unread,
        "source": "NOTIFICATION_SERVICE",
    })


if __name__ == "__main__":
    print("🔔 Notification Service starting on port 8003...")
    app.run(port=8003, debug=True)
