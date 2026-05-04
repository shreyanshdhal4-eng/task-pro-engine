from flask import Flask, request
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

conn = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = conn.cursor()

# -------------------
# TABLES
# -------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    xp INTEGER DEFAULT 0,
    streak INTEGER DEFAULT 0,
    last_completed TEXT,
    is_admin INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    text TEXT,
    completed INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS admin_requests (
    username TEXT
)
""")

conn.commit()

# -------------------
@app.route("/")
def home():
    return "backend is running"

# -------------------
# AUTH
# -------------------
@app.route("/signup", methods=["POST"])
def signup():
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (request.json["username"], request.json["password"])
        )
        conn.commit()
        return {"status": "created"}
    except:
        return {"error": "user exists"}

@app.route("/login", methods=["POST"])
def login():
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (request.json["username"], request.json["password"])
    )
    user = cursor.fetchone()

    if user:
        return {
            "token": request.json["username"],
            "is_admin": user[5]   # 👈 IMPORTANT
        }

    return {"error": "invalid"}

# -------------------
# TASKS
# -------------------
@app.route("/tasks", methods=["POST"])
def tasks():
    user = request.json["token"]
    rows = cursor.execute("SELECT * FROM tasks WHERE user=?", (user,)).fetchall()

    return [
        {"id": r[0], "text": r[2], "completed": r[3]}
        for r in rows
    ]

@app.route("/task/add", methods=["POST"])
def add():
    cursor.execute(
        "INSERT INTO tasks (user, text) VALUES (?, ?)",
        (request.json["token"], request.json["text"])
    )
    conn.commit()
    return {"status": "added"}

@app.route("/task/delete", methods=["POST"])
def delete():
    cursor.execute("DELETE FROM tasks WHERE id=?", (request.json["id"],))
    conn.commit()
    return {"status": "deleted"}

@app.route("/task/complete", methods=["POST"])
def complete():
    task_id = request.json["id"]

    cursor.execute("UPDATE tasks SET completed=1 WHERE id=?", (task_id,))
    user = cursor.execute("SELECT user FROM tasks WHERE id=?", (task_id,)).fetchone()[0]

    xp, streak, last = cursor.execute(
        "SELECT xp, streak, last_completed FROM users WHERE username=?",
        (user,)
    ).fetchone()

    today = datetime.now().strftime("%Y-%m-%d")

    if last != today:
        streak += 1

    xp += 10

    cursor.execute("""
    UPDATE users SET xp=?, streak=?, last_completed=?
    WHERE username=?
    """, (xp, streak, today, user))

    conn.commit()
    return {"xp": xp}

# -------------------
# USER STATS
# -------------------
@app.route("/user/stats", methods=["POST"])
def user_stats():
    user = request.json["token"]

    xp, streak = cursor.execute(
        "SELECT xp, streak FROM users WHERE username=?",
        (user,)
    ).fetchone()

    level = xp // 50

    return {"xp": xp, "level": level, "streak": streak}

# -------------------
# DASHBOARD
# -------------------
@app.route("/stats", methods=["POST"])
def stats():
    user = request.json["token"]

    total = cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE user=?",
        (user,)
    ).fetchone()[0]

    done = cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE user=? AND completed=1",
        (user,)
    ).fetchone()[0]

    return {"total": total, "completed": done}

# -------------------
# ADMIN SYSTEM
# -------------------
@app.route("/admin/request", methods=["POST"])
def request_admin():
    user = request.json["token"]

    cursor.execute(
        "INSERT INTO admin_requests (username) VALUES (?)",
        (user,)
    )
    conn.commit()

    return {"status": "requested"}

@app.route("/admin/requests", methods=["POST"])
def get_requests():
    rows = cursor.execute("SELECT * FROM admin_requests").fetchall()
    return [{"username": r[0]} for r in rows]

@app.route("/admin/approve", methods=["POST"])
def approve():
    username = request.json["username"]

    cursor.execute(
        "UPDATE users SET is_admin=1 WHERE username=?",
        (username,)
    )
    cursor.execute(
        "DELETE FROM admin_requests WHERE username=?",
        (username,)
    )
    conn.commit()

    return {"status": "approved"}

# -------------------
if __name__ == "__main__":
    app.run(debug=True)
