import sqlite3
from datetime import datetime, timedelta, timezone

from flask import Flask, g, jsonify, request

DB_PATH = "water.db"
DAILY_GOAL_CUPS = 8

# Maps an NFC tag's identifier to how many ml it pours, so different
# bottles/cups can each carry their own tag.
TAG_SIZES_ML = {
    "default": 250,
}

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
            ts TEXT NOT NULL,
            tag_id TEXT NOT NULL DEFAULT 'default',
            cup_ml INTEGER NOT NULL DEFAULT 250
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            date TEXT PRIMARY KEY,
            text TEXT NOT NULL
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
    body = request.get_json(silent=True) or {}
    tag_id = body.get("tag_id", "default")
    cup_ml = TAG_SIZES_ML.get(tag_id, TAG_SIZES_ML["default"])

    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    db.execute(
        "INSERT INTO events (ts, tag_id, cup_ml) VALUES (?, ?, ?)", (now, tag_id, cup_ml)
    )
    db.commit()
    return jsonify({"logged": True, "ts": now, "tag_id": tag_id, "cup_ml": cup_ml}), 201


@app.route("/tags", methods=["GET"])
def list_tags():
    return jsonify(TAG_SIZES_ML)


@app.route("/notes/<date>", methods=["GET", "PUT"])
def notes(date):
    db = get_db()
    if request.method == "PUT":
        text = (request.get_json(silent=True) or {}).get("text", "")
        db.execute(
            "INSERT INTO notes (date, text) VALUES (?, ?) "
            "ON CONFLICT(date) DO UPDATE SET text = excluded.text",
            (date, text),
        )
        db.commit()
        return jsonify({"date": date, "text": text})

    row = db.execute("SELECT text FROM notes WHERE date = ?", (date,)).fetchone()
    return jsonify({"date": date, "text": row["text"] if row else ""})


@app.route("/undo", methods=["POST"])
def undo_last():
    db = get_db()
    row = db.execute("SELECT id FROM events ORDER BY id DESC LIMIT 1").fetchone()
    if row is None:
        return jsonify({"undone": False, "reason": "no events"}), 404
    db.execute("DELETE FROM events WHERE id = ?", (row["id"],))
    db.commit()
    return jsonify({"undone": True, "id": row["id"]})


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


@app.route("/summary", methods=["GET"])
def summary():
    period = request.args.get("period", default="week")
    days = 30 if period == "month" else 7
    db = get_db()
    today = datetime.now(timezone.utc).date()
    days_data = []
    for offset in range(days - 1, -1, -1):
        day = today - timedelta(days=offset)
        days_data.append({"date": day.isoformat(), "cups": cups_on(db, day)})
    total = sum(d["cups"] for d in days_data)
    return jsonify(
        {
            "period": period,
            "days": days_data,
            "total_cups": total,
            "average_cups": round(total / days, 2),
        }
    )


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
