import sqlite3
from datetime import datetime, timedelta, timezone

from flask import Flask, g, jsonify, request

DB_PATH = "water.db"
DAILY_GOAL_CUPS = 8

app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL
        )
        """
    )
    db.commit()
    db.close()


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/log", methods=["POST"])
def log_drink():
    """Called by the iOS Shortcut when the NFC water-bottle tag is tapped."""
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    db.execute("INSERT INTO events (ts) VALUES (?)", (now,))
    db.commit()
    return jsonify({"logged": True, "ts": now}), 201


@app.route("/events", methods=["GET"])
def list_events():
    limit = request.args.get("limit", default=50, type=int)
    db = get_db()
    rows = db.execute(
        "SELECT id, ts FROM events ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.route("/today", methods=["GET"])
def today_total():
    today = datetime.now(timezone.utc).date().isoformat()
    db = get_db()
    rows = db.execute("SELECT ts FROM events WHERE ts LIKE ?", (f"{today}%",)).fetchall()
    count = len(rows)
    return jsonify(
        {
            "date": today,
            "cups": count,
            "goal": DAILY_GOAL_CUPS,
            "goal_met": count >= DAILY_GOAL_CUPS,
            "percent": round(min(count / DAILY_GOAL_CUPS, 1.0) * 100),
        }
    )


def cups_on(db, day):
    rows = db.execute("SELECT 1 FROM events WHERE ts LIKE ?", (f"{day.isoformat()}%",)).fetchall()
    return len(rows)


@app.route("/streak", methods=["GET"])
def streak():
    db = get_db()
    streak_days = 0
    day = datetime.now(timezone.utc).date()
    while cups_on(db, day) >= DAILY_GOAL_CUPS:
        streak_days += 1
        day -= timedelta(days=1)
    return jsonify({"streak_days": streak_days})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
