from flask import Flask, request, jsonify
import uuid
import hashlib
from datetime import datetime

app = Flask(__name__)

# =========================
# IN-MEMORY DATABASE (replace with MongoDB later)
# =========================
DB = {
    "users": {}
}


# =========================
# AUTH HELPERS
# =========================
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def create_token(user):
    return hashlib.md5((user + str(uuid.uuid4())).encode()).hexdigest()


# =========================
# SIGNUP
# =========================
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    u = data["username"]
    p = data["password"]

    if u in DB["users"]:
        return jsonify({"error": "User exists"}), 400

    DB["users"][u] = {
        "password": hash_pw(p),
        "tasks": [],
        "workspace": "default",
        "plan": "free",
        "token": None
    }

    return jsonify({"message": "created"})


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    u = data["username"]
    p = data["password"]

    if u not in DB["users"]:
        return jsonify({"error": "invalid"}), 401

    if DB["users"][u]["password"] != hash_pw(p):
        return jsonify({"error": "invalid"}), 401

    token = create_token(u)
    DB["users"][u]["token"] = token

    return jsonify({"token": token})


# =========================
# AUTH CHECK
# =========================
def auth_user(token):
    for u, data in DB["users"].items():
        if data.get("token") == token:
            return u
    return None


# =========================
# ADD TASK
# =========================
@app.route("/task/add", methods=["POST"])
def add_task():
    data = request.json
    token = data["token"]
    text = data["text"]

    user = auth_user(token)
    if not user:
        return jsonify({"error": "unauthorized"}), 401

    task = {
        "id": str(uuid.uuid4()),
        "text": text,
        "done": False,
        "created": str(datetime.now())
    }

    DB["users"][user]["tasks"].append(task)

    return jsonify({"task": task})


# =========================
# GET TASKS
# =========================
@app.route("/tasks", methods=["POST"])
def get_tasks():
    token = request.json["token"]

    user = auth_user(token)
    if not user:
        return jsonify({"error": "unauthorized"}), 401

    return jsonify(DB["users"][user]["tasks"])


# =========================
# TOGGLE TASK
# =========================
@app.route("/task/toggle", methods=["POST"])
def toggle():
    data = request.json
    token = data["token"]
    tid = data["id"]

    user = auth_user(token)
    if not user:
        return jsonify({"error": "unauthorized"}), 401

    for t in DB["users"][user]["tasks"]:
        if t["id"] == tid:
            t["done"] = not t["done"]

    return jsonify({"status": "updated"})


# =========================
# DELETE TASK
# =========================
@app.route("/task/delete", methods=["POST"])
def delete():
    data = request.json
    token = data["token"]
    tid = data["id"]

    user = auth_user(token)
    if not user:
        return jsonify({"error": "unauthorized"}), 401

    DB["users"][user]["tasks"] = [
        t for t in DB["users"][user]["tasks"] if t["id"] != tid
    ]

    return jsonify({"status": "deleted"})


# =========================
# RUN SERVER
# =========================
@app.route("/")
def home():
    return "Backend is running!"
if __name__ == "__main__":
        app.run(debug=True)
