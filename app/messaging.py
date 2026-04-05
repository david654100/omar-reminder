"""Twilio WhatsApp messaging."""

import logging

from twilio.rest import Client

from app import config

log = logging.getLogger(__name__)

_client: Client | None = None


def _get_client() -> Client:
    global _client
    if _client is None:
        _client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
    return _client


def send_whatsapp(body: str) -> None:
    """Send a WhatsApp message to the configured phone number."""
    preview = body[:80].replace("\n", " ")
    try:
        msg = _get_client().messages.create(
            from_=config.TWILIO_WHATSAPP_NUMBER,
            to=config.MY_PHONE_NUMBER,
            body=body,
        )
        log.info(
            "WhatsApp sent to %s [sid=%s]: %s%s",
            config.MY_PHONE_NUMBER,
            msg.sid,
            preview,
            "…" if len(body) > 80 else "",
        )
    except Exception:
        log.exception(
            "Failed to send WhatsApp to %s: %s%s",
            config.MY_PHONE_NUMBER,
            preview,
            "…" if len(body) > 80 else "",
        )
