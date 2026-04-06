"""APScheduler jobs: evening reminders at tzet hakochavim and morning follow-ups."""

import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler

from app import config
from app.messaging import send_sms
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

    send_sms(format_night_message(omer_day))
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

    send_sms(format_morning_message(omer_day))
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

    scheduler.start()
    log.info("Scheduler started.")

    # Run now in case server started after 3 PM
    _schedule_evening_reminder()
