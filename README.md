# sixty-seven — NFC Water Tracker 💧

![CI](https://github.com/jvarghesetech/sixty-seven/actions/workflows/ci.yml/badge.svg)

Tap an NFC tag stuck to your water bottle and it logs a drink — no app to
open, just tap and go. Built with Flask + SQLite, driven by an iOS Shortcuts
NFC automation.

## Features

- Log a drink event with a timestamp (`POST /log`)
- List logged drinks (`GET /events`)
- Daily total vs. goal (`GET /today`)
- Streak counter for consecutive goal-met days (`GET /streak`)
- Weekly/monthly summary (`GET /summary?period=week|month`)
- Undo the last log (`POST /undo`)
- Multiple tags with different cup sizes (`GET /tags`)
- Per-day notes (`GET/PUT /notes/<date>`)
- Config file for goal, units, and tag sizes (`config.json`)
- CSV/JSON export (`GET /export?format=csv|json`)
- Inactivity reminder check (`GET /reminder`)
- API token authentication for write endpoints
- Simple web dashboard (`GET /`)
- 7-day intake chart on the dashboard
- 30-day stats: best/worst/average cups (`GET /stats`)
- Sample data seeding script for demos (`seed_data.py`)
- Unit tests (`tests/`)
- Dockerfile for containerized deployment
- GitHub Actions CI
- iOS Shortcuts setup guide for the physical NFC tag (`ios-shortcut/SETUP.md`)

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export WATER_API_TOKEN="pick-a-long-random-string"
python app.py
```

Then open `http://localhost:5000/` for the dashboard.

To wire up the actual NFC tag on your water bottle, follow
[`ios-shortcut/SETUP.md`](ios-shortcut/SETUP.md).

## Try it with sample data

```bash
python seed_data.py
```

## Run tests

```bash
pytest tests/ -q
```

## Run with Docker

```bash
docker build -t water-tracker .
docker run -p 5000:5000 -e WATER_API_TOKEN=your-token water-tracker
```
