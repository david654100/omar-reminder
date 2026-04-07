"""Tests for SMS/email messaging and Gmail reply polling."""

from email.mime.text import MIMEText
from unittest import mock

import pytest

import app.messaging as messaging


def _simple_plain_rfc822(body: str = "YES") -> bytes:
    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = "test@gmail.com"
    msg["To"] = "test@gmail.com"
    msg["Subject"] = "test"
    return msg.as_bytes()


@mock.patch("app.messaging.smtplib.SMTP")
def test_send_email_success(mock_smtp_class):
    mock_server = mock.MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_server

    assert messaging.send_email("Subject", "body text") is True
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once()
    mock_server.send_message.assert_called_once()


@mock.patch("app.messaging.smtplib.SMTP")
def test_send_email_returns_false_on_smtp_error(mock_smtp_class):
    import smtplib

    mock_server = mock.MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_server
    mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"bad")

    assert messaging.send_email("S", "b") is False


@mock.patch("app.messaging.smtplib.SMTP")
def test_send_email_raise_on_error(mock_smtp_class):
    import smtplib

    mock_server = mock.MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_server
    mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"bad")

    with pytest.raises(smtplib.SMTPAuthenticationError):
        messaging.send_email("S", "b", raise_on_error=True)


@mock.patch("app.messaging.send_email")
@mock.patch("app.messaging.send_sms")
def test_send_notification_calls_sms_and_email(mock_send_sms, mock_send_email):
    messaging.send_notification("hello", subject="Night 1")
    mock_send_sms.assert_called_once_with("hello")
    mock_send_email.assert_called_once_with("Night 1", "hello")


def test_extract_text_body_plain():
    raw = _simple_plain_rfc822("yes please")
    text = messaging._extract_text_body(raw)
    assert text.strip().lower().startswith("yes")


@mock.patch("app.messaging.imaplib.IMAP4_SSL")
def test_fetch_email_reply_commands_empty_inbox(mock_imap_class):
    mock_mail = mock.MagicMock()
    mock_imap_class.return_value.__enter__.return_value = mock_mail
    mock_mail.search.return_value = ("OK", [b""])

    assert messaging.fetch_email_reply_commands() == []


@mock.patch("app.messaging.imaplib.IMAP4_SSL")
def test_fetch_email_reply_commands_yes(mock_imap_class):
    mock_mail = mock.MagicMock()
    mock_imap_class.return_value.__enter__.return_value = mock_mail
    mock_mail.search.return_value = ("OK", [b"42"])
    raw = _simple_plain_rfc822("YES")
    mock_mail.fetch.return_value = ("OK", [(b"42 (RFC822 {999})", raw)])

    assert messaging.fetch_email_reply_commands() == ["yes"]


@mock.patch("app.messaging.imaplib.IMAP4_SSL")
def test_fetch_email_reply_commands_status(mock_imap_class):
    mock_mail = mock.MagicMock()
    mock_imap_class.return_value.__enter__.return_value = mock_mail
    mock_mail.search.return_value = ("OK", [b"7"])
    raw = _simple_plain_rfc822("STATUS")
    mock_mail.fetch.return_value = ("OK", [(b"7 (RFC822 {999})", raw)])

    assert messaging.fetch_email_reply_commands() == ["status"]


@mock.patch("app.messaging.imaplib.IMAP4_SSL")
def test_fetch_email_reply_commands_ignores_unknown_body(mock_imap_class):
    mock_mail = mock.MagicMock()
    mock_imap_class.return_value.__enter__.return_value = mock_mail
    mock_mail.search.return_value = ("OK", [b"1"])
    raw = _simple_plain_rfc822("hello there")
    mock_mail.fetch.return_value = ("OK", [(b"1 (RFC822 {999})", raw)])

    assert messaging.fetch_email_reply_commands() == []


@mock.patch("app.messaging.imaplib.IMAP4_SSL")
def test_fetch_email_reply_commands_returns_empty_on_imap_error(mock_imap_class):
    mock_imap_class.side_effect = OSError("network down")

    assert messaging.fetch_email_reply_commands() == []
