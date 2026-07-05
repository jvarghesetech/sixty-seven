import importlib
import os

import pytest


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config.json").write_text(
        '{"daily_goal_cups": 2, "unit": "cups", "reminder_after_hours": 3, '
        '"tag_sizes_ml": {"default": 250}}'
    )
    import app as app_module

    importlib.reload(app_module)
    app_module.init_db()
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_log_and_list_events(client):
    resp = client.post("/log")
    assert resp.status_code == 201
    assert resp.get_json()["logged"] is True

    resp = client.get("/events")
    assert len(resp.get_json()) == 1


def test_today_goal_met(client):
    client.post("/log")
    client.post("/log")
    resp = client.get("/today")
    data = resp.get_json()
    assert data["cups"] == 2
    assert data["goal_met"] is True


def test_undo(client):
    client.post("/log")
    resp = client.post("/undo")
    assert resp.get_json()["undone"] is True
    assert client.get("/events").get_json() == []


def test_undo_with_no_events(client):
    resp = client.post("/undo")
    assert resp.status_code == 404
