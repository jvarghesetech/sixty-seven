import sqlite3
from datetime import datetime, timezone

from flask import Flask, g, jsonify, request

DB_PATH = "water.db"

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


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
