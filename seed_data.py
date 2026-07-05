"""Populate water.db with fake historical drink events for demos/testing."""
import random
import sqlite3
from datetime import datetime, timedelta, timezone

from app import DB_PATH, init_db

TAGS = ["default", "big-bottle", "office-cup"]


def seed(days=30, min_per_day=3, max_per_day=10):
    init_db()
    db = sqlite3.connect(DB_PATH)
    today = datetime.now(timezone.utc).date()
    for offset in range(days):
        day = today - timedelta(days=offset)
        for _ in range(random.randint(min_per_day, max_per_day)):
            hour = random.randint(7, 22)
            minute = random.randint(0, 59)
            ts = datetime(day.year, day.month, day.day, hour, minute, tzinfo=timezone.utc)
            tag_id = random.choice(TAGS)
            db.execute(
                "INSERT INTO events (ts, tag_id, cup_ml) VALUES (?, ?, ?)",
                (ts.isoformat(), tag_id, 250),
            )
    db.commit()
    db.close()
    print(f"Seeded {days} days of sample water-drinking data into {DB_PATH}")


if __name__ == "__main__":
    seed()
