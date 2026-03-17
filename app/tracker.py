"""SQLite-based tracker for Omer counting confirmations."""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "omer_tracker.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    """Create the tracking tables if they don't exist."""
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS omer_counts (
            omer_day INTEGER PRIMARY KEY,
            counted_at TEXT NOT NULL,
            with_bracha INTEGER NOT NULL DEFAULT 1,
            reminder_type TEXT NOT NULL DEFAULT 'night'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reminders_sent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            omer_day INTEGER NOT NULL,
            reminder_type TEXT NOT NULL,
            sent_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def record_count(omer_day: int, with_bracha: bool = True, reminder_type: str = "night") -> bool:
    """
    Record that the user counted for the given Omer day.
    Returns True if newly recorded, False if already recorded.
    """
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT INTO omer_counts (omer_day, counted_at, with_bracha, reminder_type) VALUES (?, ?, ?, ?)",
            (omer_day, datetime.now().isoformat(), int(with_bracha), reminder_type),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def record_reminder_sent(omer_day: int, reminder_type: str) -> None:
    """Record that a reminder was sent."""
    conn = _get_conn()
    conn.execute(
        "INSERT INTO reminders_sent (omer_day, reminder_type, sent_at) VALUES (?, ?, ?)",
        (omer_day, reminder_type, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def was_counted(omer_day: int) -> bool:
    """Check if the given Omer day was counted."""
    conn = _get_conn()
    row = conn.execute("SELECT 1 FROM omer_counts WHERE omer_day = ?", (omer_day,)).fetchone()
    conn.close()
    return row is not None


def was_reminder_sent(omer_day: int, reminder_type: str) -> bool:
    """Check if a reminder of the given type was already sent for this day."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT 1 FROM reminders_sent WHERE omer_day = ? AND reminder_type = ?",
        (omer_day, reminder_type),
    ).fetchone()
    conn.close()
    return row is not None


def get_pending_day() -> tuple[int, bool] | None:
    """
    Figure out which Omer day is pending confirmation by looking at reminders
    sent but not yet counted. Returns (omer_day, with_bracha) or None.
    """
    conn = _get_conn()
    row = conn.execute("""
        SELECT r.omer_day, r.reminder_type
        FROM reminders_sent r
        LEFT JOIN omer_counts c ON r.omer_day = c.omer_day
        WHERE c.omer_day IS NULL
        ORDER BY r.sent_at DESC
        LIMIT 1
    """).fetchone()
    conn.close()
    if row is None:
        return None
    with_bracha = row["reminder_type"] == "night"
    return (row["omer_day"], with_bracha)


def get_all_counts() -> list[dict]:
    """Return all recorded counts as a list of dicts."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT omer_day, counted_at, with_bracha, reminder_type FROM omer_counts ORDER BY omer_day"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_total_counted() -> int:
    conn = _get_conn()
    row = conn.execute("SELECT COUNT(*) as cnt FROM omer_counts").fetchone()
    conn.close()
    return row["cnt"]


def get_current_streak() -> int:
    """Calculate the current consecutive counting streak (backwards from most recent)."""
    conn = _get_conn()
    rows = conn.execute("SELECT omer_day FROM omer_counts ORDER BY omer_day DESC").fetchall()
    conn.close()
    if not rows:
        return 0
    days = [r["omer_day"] for r in rows]
    streak = 1
    for i in range(len(days) - 1):
        if days[i] - days[i + 1] == 1:
            streak += 1
        else:
            break
    return streak
