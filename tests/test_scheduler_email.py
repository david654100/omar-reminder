"""Tests for scheduler email reply processing and notification wiring."""

from unittest import mock

import pytest

from app import tracker
from app.scheduler import _process_email_replies, _send_evening_reminder, _send_morning_followup


@pytest.fixture
def db(tmp_path):
    with mock.patch.object(tracker, "DB_PATH", tmp_path / "scheduler_email.db"):
        tracker.init_db()
        yield


@mock.patch("app.scheduler.send_email", return_value=True)
@mock.patch("app.scheduler.fetch_email_reply_commands", return_value=["yes"])
def test_process_email_yes_records_pending_day(mock_fetch, mock_send_email, db):
    tracker.record_reminder_sent(12, "night")
    assert not tracker.was_counted(12)

    _process_email_replies()

    assert tracker.was_counted(12)
    mock_send_email.assert_not_called()


@mock.patch("app.scheduler.send_email", return_value=True)
@mock.patch("app.scheduler.fetch_email_reply_commands", return_value=["yes"])
@mock.patch("app.scheduler.get_omer_day", return_value=8)
def test_process_email_yes_without_pending_uses_omer_day(mock_omer, mock_fetch, mock_send_email, db):
    _process_email_replies()
    assert tracker.was_counted(8)


@mock.patch("app.scheduler.send_email", return_value=True)
@mock.patch("app.scheduler.fetch_email_reply_commands", return_value=["status"])
def test_process_email_status_sends_email(mock_fetch, mock_send_email, db):
    _process_email_replies()

    mock_send_email.assert_called_once()
    subject, body = mock_send_email.call_args[0]
    assert subject == "Omer Counting Status"
    assert "Total counted:" in body
    assert "Current streak:" in body


@mock.patch("app.scheduler.send_email")
@mock.patch("app.scheduler.fetch_email_reply_commands", return_value=[])
def test_process_email_no_commands_no_op(mock_fetch, mock_send_email, db):
    _process_email_replies()
    mock_send_email.assert_not_called()


@mock.patch("app.scheduler.send_notification")
@mock.patch("app.scheduler.get_omer_day", return_value=3)
def test_send_evening_reminder_calls_send_notification_and_records(mock_omer, mock_notify, db):
    assert not tracker.was_reminder_sent(3, "night")

    _send_evening_reminder()

    mock_notify.assert_called_once()
    (body,) = mock_notify.call_args.args
    assert "Night 3 of the Omer" in body
    assert mock_notify.call_args.kwargs["subject"] == "Omer Day 3 - Count Tonight"
    assert tracker.was_reminder_sent(3, "night")


@mock.patch("app.scheduler.send_notification")
@mock.patch("app.scheduler.get_omer_day", return_value=3)
def test_send_evening_reminder_skips_if_already_sent(mock_omer, mock_notify, db):
    tracker.record_reminder_sent(3, "night")
    _send_evening_reminder()
    mock_notify.assert_not_called()


@mock.patch("app.scheduler.send_notification")
@mock.patch("app.scheduler.should_skip_morning", return_value=False)
@mock.patch("app.scheduler.get_omer_day", return_value=4)
def test_send_morning_followup_calls_send_notification(mock_omer, mock_skip, mock_notify, db):
    _send_morning_followup()

    mock_notify.assert_called_once()
    (body,) = mock_notify.call_args.args
    assert "Day 4 of the Omer" in body or "missed" in body.lower()
    assert mock_notify.call_args.kwargs["subject"] == "Omer Day 4 - Missed Last Night"
    assert tracker.was_reminder_sent(4, "morning")
