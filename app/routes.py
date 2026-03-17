"""Flask routes: WhatsApp webhook and web dashboard."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from flask import Blueprint, render_template, request
from twilio.twiml.messaging_response import MessagingResponse

from app import config, tracker
from app.omer import get_omer_day
from app.zmanim import get_tzet_hakochavim

bp = Blueprint("main", __name__)


@bp.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming WhatsApp messages from Twilio."""
    body = request.form.get("Body", "").strip().lower()
    resp = MessagingResponse()

    if body in ("yes", "y", "counted", "done"):
        pending = tracker.get_pending_day()

        if pending is None:
            tz = ZoneInfo(config.TIMEZONE)
            today = datetime.now(tz).date()
            omer_day = get_omer_day(today) or get_omer_day(today - timedelta(days=1))
            if omer_day is None:
                resp.message("No active Omer day to record.")
                return str(resp)
            with_bracha = True
        else:
            omer_day, with_bracha = pending

        is_new = tracker.record_count(omer_day, with_bracha=with_bracha)
        total = tracker.get_total_counted()
        streak = tracker.get_current_streak()

        if is_new:
            bracha_note = "" if with_bracha else " (without bracha)"
            resp.message(
                f"✅ Recorded day {omer_day}{bracha_note}!\n"
                f"Total counted: {total}/49 | Streak: {streak} days"
            )
        else:
            resp.message(
                f"Day {omer_day} was already recorded.\n"
                f"Total counted: {total}/49 | Streak: {streak} days"
            )

    elif body in ("status", "stats", "history"):
        total = tracker.get_total_counted()
        streak = tracker.get_current_streak()
        counts = tracker.get_all_counts()
        days_list = ", ".join(str(c["omer_day"]) for c in counts) or "None yet"

        resp.message(
            f"📊 *Omer Counting Status*\n\n"
            f"Total counted: {total}/49\n"
            f"Current streak: {streak} days\n"
            f"Days counted: {days_list}"
        )

    else:
        resp.message(
            "Reply *YES* to confirm you counted the Omer.\n"
            "Reply *STATUS* to see your counting history."
        )

    return str(resp)


@bp.route("/")
def dashboard():
    """Render the web dashboard."""
    tz = ZoneInfo(config.TIMEZONE)
    today = datetime.now(tz).date()
    omer_day = get_omer_day(today)
    tzet = get_tzet_hakochavim(today)

    counts = tracker.get_all_counts()
    counted_set = {c["omer_day"] for c in counts}
    bracha_map = {c["omer_day"]: bool(c["with_bracha"]) for c in counts}

    total = tracker.get_total_counted()
    streak = tracker.get_current_streak()
    tzet_str = tzet.strftime("%I:%M %p") if tzet else "N/A"

    return render_template(
        "dashboard.html",
        omer_day=omer_day,
        today=today,
        tzet_str=tzet_str,
        counted_set=counted_set,
        bracha_map=bracha_map,
        total=total,
        streak=streak,
    )
