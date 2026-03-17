"""Tests for Flask routes (webhook and dashboard)."""

from unittest import mock

import pytest

from app import create_app, tracker


@pytest.fixture
def client(tmp_path):
    """Create a Flask test client with a temp database."""
    with mock.patch.object(tracker, "DB_PATH", tmp_path / "test.db"):
        app = create_app()
        app.config["TESTING"] = True
        tracker.init_db()
        with app.test_client() as c:
            yield c


class TestWebhook:
    def test_yes_with_pending_day(self, client):
        tracker.record_reminder_sent(10, "night")
        response = client.post("/webhook", data={"Body": "yes"})
        assert response.status_code == 200
        assert b"Recorded day 10" in response.data

    @mock.patch("app.routes.get_omer_day", return_value=10)
    def test_yes_duplicate(self, mock_omer_day, client):
        tracker.record_reminder_sent(10, "night")
        tracker.record_count(10)
        response = client.post("/webhook", data={"Body": "yes"})
        assert response.status_code == 200
        assert b"already recorded" in response.data

    def test_status_command(self, client):
        tracker.record_reminder_sent(1, "night")
        tracker.record_count(1)
        response = client.post("/webhook", data={"Body": "status"})
        assert response.status_code == 200
        assert b"Omer Counting Status" in response.data
        assert b"1/49" in response.data

    def test_unknown_command(self, client):
        response = client.post("/webhook", data={"Body": "hello"})
        assert response.status_code == 200
        assert b"Reply" in response.data

    def test_morning_yes_no_bracha(self, client):
        tracker.record_reminder_sent(5, "morning")
        response = client.post("/webhook", data={"Body": "y"})
        assert response.status_code == 200
        assert b"without bracha" in response.data


class TestDashboard:
    @mock.patch("app.routes.get_tzet_hakochavim")
    @mock.patch("app.routes.get_omer_day")
    def test_dashboard_loads(self, mock_omer_day, mock_tzet, client):
        mock_omer_day.return_value = 10
        mock_tzet.return_value = None
        response = client.get("/")
        assert response.status_code == 200
        assert b"Sefirat HaOmer" in response.data

    @mock.patch("app.routes.get_tzet_hakochavim")
    @mock.patch("app.routes.get_omer_day")
    def test_dashboard_outside_omer(self, mock_omer_day, mock_tzet, client):
        mock_omer_day.return_value = None
        mock_tzet.return_value = None
        response = client.get("/")
        assert response.status_code == 200
        assert b"Not currently in the Omer period" in response.data
