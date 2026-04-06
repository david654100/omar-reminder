"""Twilio SMS messaging."""

import logging

from twilio.rest import Client

from app import config

log = logging.getLogger(__name__)

_client: Client | None = None

SMS_MAX_LENGTH = 1600


def _get_client() -> Client:
    global _client
    if _client is None:
        _client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
    return _client


def send_sms(body: str) -> None:
    """Send an SMS via Twilio. Truncates if the body exceeds 1600 chars."""
    if len(body) > SMS_MAX_LENGTH:
        body = body[: SMS_MAX_LENGTH - 30] + "\n\n(message truncated)"

    preview = body[:80].replace("\n", " ")
    suffix = "…" if len(body) > 80 else ""
    try:
        msg = _get_client().messages.create(
            from_=config.TWILIO_PHONE_NUMBER,
            to=config.MY_PHONE_NUMBER,
            body=body,
        )
        log.info("SMS sent [sid=%s]: %s%s", msg.sid, preview, suffix)
    except Exception:
        log.exception("Failed to send SMS: %s%s", preview, suffix)
