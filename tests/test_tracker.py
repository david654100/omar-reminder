"""Tests for the SQLite tracker."""

import sqlite3
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from app import tracker


@pytest.fixture(autouse=True)
def use_temp_db(tmp_path):
    """Redirect the tracker to use a temp database for each test."""
    test_db = tmp_path / "test_omer.db"
    with mock.patch.object(tracker, "DB_PATH", test_db):
        tracker.init_db()
        yield


class TestInitDb:
    def test_creates_tables(self, tmp_path):
        db_path = tmp_path / "init_test.db"
        with mock.patch.object(tracker, "DB_PATH", db_path):
            tracker.init_db()
        conn = sqlite3.connect(str(db_path))
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = {t[0] for t in tables}
        conn.close()
        assert "omer_counts" in table_names
        assert "reminders_sent" in table_names


class TestRecordCount:
    def test_record_new_count(self):
        assert tracker.record_count(1) is True

    def test_duplicate_returns_false(self):
        tracker.record_count(1)
        assert tracker.record_count(1) is False

    def test_different_days_both_succeed(self):
        assert tracker.record_count(1) is True
        assert tracker.record_count(2) is True

    def test_without_bracha(self):
        tracker.record_count(5, with_bracha=False, reminder_type="morning")
        counts = tracker.get_all_counts()
        assert len(counts) == 1
        assert counts[0]["with_bracha"] == 0
        assert counts[0]["reminder_type"] == "morning"


class TestWasCounted:
    def test_not_counted(self):
        assert tracker.was_counted(1) is False

    def test_counted(self):
        tracker.record_count(1)
        assert tracker.was_counted(1) is True


class TestReminderSent:
    def test_not_sent(self):
        assert tracker.was_reminder_sent(1, "night") is False

    def test_sent(self):
        tracker.record_reminder_sent(1, "night")
        assert tracker.was_reminder_sent(1, "night") is True

    def test_different_types_independent(self):
        tracker.record_reminder_sent(1, "night")
        assert tracker.was_reminder_sent(1, "morning") is False


class TestGetPendingDay:
    def test_no_pending(self):
        assert tracker.get_pending_day() is None

    def test_night_reminder_pending(self):
        tracker.record_reminder_sent(5, "night")
        result = tracker.get_pending_day()
        assert result == (5, True)

    def test_morning_reminder_pending(self):
        tracker.record_reminder_sent(5, "morning")
        result = tracker.get_pending_day()
        assert result == (5, False)

    def test_counted_day_not_pending(self):
        tracker.record_reminder_sent(5, "night")
        tracker.record_count(5)
        assert tracker.get_pending_day() is None

    def test_most_recent_uncounted_returned(self):
        tracker.record_reminder_sent(3, "night")
        tracker.record_count(3)
        tracker.record_reminder_sent(4, "night")
        result = tracker.get_pending_day()
        assert result == (4, True)


class TestGetAllCounts:
    def test_empty(self):
        assert tracker.get_all_counts() == []

    def test_returns_ordered(self):
        tracker.record_count(3)
        tracker.record_count(1)
        tracker.record_count(2)
        counts = tracker.get_all_counts()
        days = [c["omer_day"] for c in counts]
        assert days == [1, 2, 3]


class TestGetTotalCounted:
    def test_zero_initially(self):
        assert tracker.get_total_counted() == 0

    def test_counts_correctly(self):
        tracker.record_count(1)
        tracker.record_count(2)
        tracker.record_count(3)
        assert tracker.get_total_counted() == 3


class TestGetCurrentStreak:
    def test_no_counts(self):
        assert tracker.get_current_streak() == 0

    def test_single_day(self):
        tracker.record_count(1)
        assert tracker.get_current_streak() == 1

    def test_consecutive_days(self):
        for d in range(1, 6):
            tracker.record_count(d)
        assert tracker.get_current_streak() == 5

    def test_broken_streak(self):
        tracker.record_count(1)
        tracker.record_count(2)
        # skip day 3
        tracker.record_count(4)
        tracker.record_count(5)
        assert tracker.get_current_streak() == 2

    def test_gap_then_single(self):
        tracker.record_count(1)
        tracker.record_count(5)
        assert tracker.get_current_streak() == 1
