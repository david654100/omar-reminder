"""Outbound SMS (Twilio) and email (Gmail SMTP), plus Gmail IMAP reply polling.

Reminders use :func:`send_notification` to deliver both channels. Inbound email
commands (unread messages from :attr:`config.ALLOWED_EMAIL` whose body starts
with ``yes`` or ``status``) are collected by :func:`fetch_email_reply_commands`
for the scheduler to process.
"""

import email
import imaplib
import logging
import smtplib
from email import policy
from email.mime.text import MIMEText

from twilio.rest import Client

from app import config

log = logging.getLogger(__name__)

_client: Client | None = None

SMS_MAX_LENGTH = 1600


def _get_client() -> Client:
    """Return a singleton Twilio REST client."""
    global _client
    if _client is None:
        _client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
    return _client


def send_sms(body: str) -> None:
    """Send an SMS via Twilio to ``MY_PHONE_NUMBER``.

    Long bodies are truncated to fit Twilio limits. Errors are logged and not
    re-raised.

    Args:
        body: Plain-text message body.
    """
    if len(body) > SMS_MAX_LENGTH:
        body = body[: SMS_MAX_LENGTH - 30] + "\n\n(message truncated)"

    preview = body[:80].replace("\n", " ")
    suffix = "..." if len(body) > 80 else ""
    try:
        msg = _get_client().messages.create(
            from_=config.TWILIO_PHONE_NUMBER,
            to=config.MY_PHONE_NUMBER,
            body=body,
        )
        log.info("SMS sent [sid=%s]: %s%s", msg.sid, preview, suffix)
    except Exception:
        log.exception("Failed to send SMS: %s%s", preview, suffix)


def send_email(subject: str, body: str, *, raise_on_error: bool = False) -> bool:
    """Send a plain-text email to ``ALLOWED_EMAIL`` using Gmail SMTP.

    Uses ``GMAIL_ADDRESS`` and ``GMAIL_APP_PASSWORD`` for authentication.

    Args:
        subject: Email subject line.
        body: Plain-text body.
        raise_on_error: If True, re-raise after logging; if False, return False.

    Returns:
        True if the message was sent successfully, False on failure (when
        ``raise_on_error`` is False).

    Raises:
        Exception: Any SMTP error when ``raise_on_error`` is True.
    """
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = config.GMAIL_ADDRESS
    msg["To"] = config.ALLOWED_EMAIL

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(config.GMAIL_ADDRESS, config.GMAIL_APP_PASSWORD)
            server.send_message(msg)
        log.info("Email sent to %s: %s", config.ALLOWED_EMAIL, subject)
        return True
    except Exception:
        log.exception("Failed to send email: %s", subject)
        if raise_on_error:
            raise
        return False


def send_notification(body: str, subject: str = "Omer Reminder") -> None:
    """Send the same reminder via SMS and email.

    Each channel is independent; a failure in one is logged but does not block
    the other.

    Args:
        body: Shared plain-text body for SMS and email.
        subject: Email subject (SMS has no subject).
    """
    send_sms(body)
    send_email(subject, body)


def _extract_text_body(raw_msg: bytes) -> str:
    """Best-effort decode of the first text/plain part from raw RFC822 bytes.

    Args:
        raw_msg: Full message as received from IMAP ``RFC822`` fetch.

    Returns:
        Decoded plain text, possibly empty if no suitable part exists.
    """
    msg = email.message_from_bytes(raw_msg, policy=policy.default)
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    return part.get_content()
                except Exception:
                    payload = part.get_payload(decode=True) or b""
                    return payload.decode(errors="ignore")
        return ""
    try:
        return msg.get_content()
    except Exception:
        payload = msg.get_payload(decode=True) or b""
        return payload.decode(errors="ignore")


def fetch_email_reply_commands() -> list[str]:
    """Poll Gmail for unread messages from the allowed user and parse commands.

    Searches ``INBOX`` for ``UNSEEN`` messages where the From address matches
    ``ALLOWED_EMAIL``. For each message, if the decoded body (lowercased) starts
    with ``yes`` or ``status``, appends ``\"yes\"`` or ``\"status\"`` to the
    result list. Order follows IMAP search order.

    Returns:
        A list of command strings (``\"yes\"`` / ``\"status\"``). Empty on no
        matches or on IMAP errors (errors are logged).
    """
    commands: list[str] = []
    try:
        with imaplib.IMAP4_SSL(config.GMAIL_IMAP_HOST) as mail:
            mail.login(config.GMAIL_ADDRESS, config.GMAIL_APP_PASSWORD)
            mail.select("INBOX")
            status, data = mail.search(None, '(UNSEEN FROM "{}")'.format(config.ALLOWED_EMAIL))
            if status != "OK" or not data or not data[0]:
                return commands

            for msg_id in data[0].split():
                status, fetched = mail.fetch(msg_id, "(RFC822)")
                if status != "OK" or not fetched:
                    continue
                raw = fetched[0][1]
                if not isinstance(raw, bytes):
                    continue
                body = _extract_text_body(raw).strip().lower()
                if not body:
                    continue
                if body.startswith("yes"):
                    commands.append("yes")
                elif body.startswith("status"):
                    commands.append("status")
    except Exception:
        log.exception("Failed polling Gmail replies")
    return commands
