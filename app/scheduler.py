"""APScheduler jobs: evening reminders at tzet hakochavim and morning follow-ups."""

import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler

from app import config
from app.messaging import fetch_email_reply_commands, send_email, send_notification
from app.omer import format_morning_message, format_night_message, get_omer_day
from app.zmanim import get_tzet_hakochavim, should_skip_evening, should_skip_morning
from app import tracker

log = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone=config.TIMEZONE)


def _send_evening_reminder() -> None:
    """Send the nightly Omer reminder."""
    tz = ZoneInfo(config.TIMEZONE)
    today = datetime.now(tz).date()
    omer_day = get_omer_day(today)

    if omer_day is None:
        log.info("Not in Omer period (%s). Skipping.", today)
        return

    if tracker.was_reminder_sent(omer_day, "night"):
        log.info("Night reminder already sent for day %d. Skipping.", omer_day)
        return

    send_notification(
        format_night_message(omer_day),
        subject=f"Omer Day {omer_day} - Count Tonight",
    )
    tracker.record_reminder_sent(omer_day, "night")
    log.info("Sent night reminder for Omer day %d.", omer_day)


def _send_morning_followup() -> None:
    """Send a morning follow-up if last night's count wasn't confirmed."""
    tz = ZoneInfo(config.TIMEZONE)
    today = datetime.now(tz).date()

    if should_skip_morning(today):
        log.info("Shabbat/Yom Tov morning (%s). Skipping.", today)
        return

    yesterday = today - timedelta(days=1)
    omer_day = get_omer_day(yesterday)

    if omer_day is None:
        return

    if tracker.was_counted(omer_day):
        log.info("Omer day %d already counted. No morning followup needed.", omer_day)
        return

    if tracker.was_reminder_sent(omer_day, "morning"):
        log.info("Morning reminder already sent for day %d. Skipping.", omer_day)
        return

    send_notification(
        format_morning_message(omer_day),
        subject=f"Omer Day {omer_day} - Missed Last Night",
    )
    tracker.record_reminder_sent(omer_day, "morning")
    log.info("Sent morning followup for Omer day %d.", omer_day)


def _schedule_evening_reminder() -> None:
    """
    Daily afternoon job: calculates tonight's tzet hakochavim and schedules
    the actual reminder at the exact time.
    """
    tz = ZoneInfo(config.TIMEZONE)
    today = datetime.now(tz).date()

    if should_skip_evening(today):
        log.info("Shabbat/Yom Tov evening (%s). Skipping.", today)
        return

    omer_day = get_omer_day(today)
    if omer_day is None:
        log.info("Not in Omer period (%s). Skipping.", today)
        return

    tzet = get_tzet_hakochavim(today)
    if tzet is None:
        log.warning("Could not calculate tzet hakochavim for %s.", today)
        return

    now = datetime.now(tz)
    if tzet <= now:
        log.info("Tzet hakochavim already passed. Sending immediately.")
        _send_evening_reminder()
        return

    job_id = f"evening_reminder_{today.isoformat()}"
    if scheduler.get_job(job_id):
        log.info("Evening job already scheduled for %s.", today)
        return

    scheduler.add_job(
        _send_evening_reminder,
        "date",
        run_date=tzet,
        id=job_id,
        replace_existing=True,
    )
    log.info("Scheduled Omer day %d reminder at %s.", omer_day, tzet.strftime("%I:%M %p %Z"))


def _process_email_replies() -> None:
    """Process unread Gmail replies (YES/STATUS) from ALLOWED_EMAIL."""
    commands = fetch_email_reply_commands()
    if not commands:
        return

    tz = ZoneInfo(config.TIMEZONE)
    today = datetime.now(tz).date()
    for cmd in commands:
        if cmd == "yes":
            pending = tracker.get_pending_day()
            if pending is None:
                omer_day = get_omer_day(today) or get_omer_day(today - timedelta(days=1))
                if omer_day is None:
                    continue
                with_bracha = True
            else:
                omer_day, with_bracha = pending

            is_new = tracker.record_count(omer_day, with_bracha=with_bracha)
            if is_new:
                log.info("Recorded Omer day %d from email YES reply.", omer_day)
            else:
                log.info("Email YES reply for already-recorded Omer day %d.", omer_day)
        elif cmd == "status":
            total = tracker.get_total_counted()
            streak = tracker.get_current_streak()
            counts = tracker.get_all_counts()
            days_list = ", ".join(str(c["omer_day"]) for c in counts) or "None yet"
            send_email_subject = "Omer Counting Status"
            send_email_body = (
                "Omer Counting Status\n\n"
                f"Total counted: {total}/49\n"
                f"Current streak: {streak} days\n"
                f"Days counted: {days_list}"
            )
            send_email(send_email_subject, send_email_body)
            log.info("Sent status response from email STATUS reply.")


def start() -> None:
    """Start the scheduler with daily jobs."""
    scheduler.add_job(
        _schedule_evening_reminder,
        "cron",
        hour=15,
        minute=0,
        id="daily_scheduler",
        replace_existing=True,
    )

    scheduler.add_job(
        _send_morning_followup,
        "cron",
        hour=config.MORNING_REMINDER_HOUR,
        minute=0,
        id="morning_followup",
        replace_existing=True,
    )
    scheduler.add_job(
        _process_email_replies,
        "interval",
        minutes=config.EMAIL_REPLY_POLL_MINUTES,
        id="email_reply_poll",
        replace_existing=True,
    )

    scheduler.start()
    log.info("Scheduler started.")

    # Run now in case server started after 3 PM
    _schedule_evening_reminder()
