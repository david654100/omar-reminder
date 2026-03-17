"""Tests for Flask routes (webhook, auth, and dashboard)."""

from unittest import mock

import pytest

from app import create_app, tracker


@pytest.fixture
def app(tmp_path):
    with mock.patch.object(tracker, "DB_PATH", tmp_path / "test.db"):
        application = create_app()
        application.config["TESTING"] = True
        tracker.init_db()
        yield application


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


@pytest.fixture
def authed_client(app):
    """A test client with a pre-authenticated session."""
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["user_email"] = "test@gmail.com"
            sess["user_name"] = "Test User"
            sess["user_picture"] = ""
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


class TestAuth:
    def test_dashboard_redirects_to_login(self, client):
        response = client.get("/")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_login_page_loads(self, client):
        response = client.get("/login")
        assert response.status_code == 200
        assert b"Sign in with Google" in response.data

    def test_google_redirect(self, client):
        response = client.get("/login/google")
        assert response.status_code == 302
        assert "accounts.google.com" in response.headers["Location"]

    def test_logout_clears_session(self, authed_client):
        authed_client.get("/logout")
        response = authed_client.get("/")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_already_logged_in_redirects_to_dashboard(self, authed_client):
        response = authed_client.get("/login")
        assert response.status_code == 302
        assert response.headers["Location"] == "/"


class TestDashboard:
    @mock.patch("app.routes.get_tzet_hakochavim")
    @mock.patch("app.routes.get_omer_day")
    def test_dashboard_loads(self, mock_omer_day, mock_tzet, authed_client):
        mock_omer_day.return_value = 10
        mock_tzet.return_value = None
        response = authed_client.get("/")
        assert response.status_code == 200
        assert b"Sefirat HaOmer" in response.data

    @mock.patch("app.routes.get_tzet_hakochavim")
    @mock.patch("app.routes.get_omer_day")
    def test_dashboard_outside_omer(self, mock_omer_day, mock_tzet, authed_client):
        mock_omer_day.return_value = None
        mock_tzet.return_value = None
        response = authed_client.get("/")
        assert response.status_code == 200
        assert b"Not currently in the Omer period" in response.data

    @mock.patch("app.routes.get_tzet_hakochavim")
    @mock.patch("app.routes.get_omer_day")
    def test_dashboard_shows_sign_out(self, mock_omer_day, mock_tzet, authed_client):
        mock_omer_day.return_value = None
        mock_tzet.return_value = None
        response = authed_client.get("/")
        assert b"Sign out" in response.data
