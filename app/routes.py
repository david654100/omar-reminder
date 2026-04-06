"""Flask routes: SMS webhook, Google OAuth, and web dashboard."""

import functools
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from twilio.twiml.messaging_response import MessagingResponse

from app import config, tracker
from app.omer import get_omer_dates, get_omer_day
from app.zmanim import get_tzet_hakochavim

bp = Blueprint("main", __name__)


def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_email"):
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)
    return decorated


# ─── Auth ─────────────────────────────────────────────────────────────────────


@bp.route("/login")
def login():
    if session.get("user_email"):
        return redirect(url_for("main.dashboard"))
    return render_template("login.html")


@bp.route("/login/google")
def login_google():
    from app import oauth
    redirect_uri = url_for("main.auth_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@bp.route("/auth/callback")
def auth_callback():
    from app import oauth
    token = oauth.google.authorize_access_token()
    userinfo = token.get("userinfo")

    if not userinfo or not userinfo.get("email"):
        return redirect(url_for("main.login"))

    email = userinfo["email"].lower()
    if email != config.ALLOWED_EMAIL.lower():
        session.clear()
        return render_template("login.html", error="This account is not authorized.")

    session["user_email"] = email
    session["user_name"] = userinfo.get("name", email)
    session["user_picture"] = userinfo.get("picture", "")
    return redirect(url_for("main.dashboard"))


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


# ─── Webhook (no auth — Twilio needs access) ─────────────────────────────────


@bp.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming SMS messages from Twilio."""
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


# ─── Dashboard ────────────────────────────────────────────────────────────────


@bp.route("/")
@login_required
def dashboard():
    """Render the web dashboard."""
    tz = ZoneInfo(config.TIMEZONE)
    now = datetime.now(tz)
    today = now.date()
    tonight_day = get_omer_day(today)
    last_night_day = get_omer_day(today - timedelta(days=1))
    tzet = get_tzet_hakochavim(today)

    past_nightfall = tzet is not None and now >= tzet

    if past_nightfall:
        current_day = tonight_day
    else:
        current_day = last_night_day

    counts = tracker.get_all_counts()
    counted_set = {c["omer_day"] for c in counts}
    bracha_map = {c["omer_day"]: bool(c["with_bracha"]) for c in counts}

    total = tracker.get_total_counted()
    streak = tracker.get_current_streak()
    tzet_str = tzet.strftime("%I:%M %p") if tzet else "N/A"
    omer_dates = get_omer_dates(today.year)

    return render_template(
        "dashboard.html",
        current_day=current_day,
        tonight_day=tonight_day,
        past_nightfall=past_nightfall,
        today=today,
        tzet_str=tzet_str,
        counted_set=counted_set,
        bracha_map=bracha_map,
        total=total,
        streak=streak,
        omer_dates=omer_dates,
        user_name=session.get("user_name", ""),
        user_picture=session.get("user_picture", ""),
    )


@bp.route("/override", methods=["POST"])
@login_required
def override_day():
    """Mark a missed Omer day as counted from the dashboard."""
    data = request.get_json(silent=True) or {}
    try:
        omer_day_num = int(data.get("day", 0))
    except (TypeError, ValueError):
        return jsonify(ok=False, error="Invalid day"), 400

    if not 1 <= omer_day_num <= 49:
        return jsonify(ok=False, error="Day must be 1-49"), 400

    with_bracha = bool(data.get("with_bracha", False))
    is_new = tracker.record_count(omer_day_num, with_bracha=with_bracha, reminder_type="manual")

    return jsonify(ok=True, is_new=is_new)


# ─── Legal Pages (public) ─────────────────────────────────────────────────


@bp.route("/privacy")
def privacy():
    return render_template("privacy.html")


@bp.route("/terms")
def terms():
    return render_template("terms.html")
