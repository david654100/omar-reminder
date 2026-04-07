"""Pytest plugin: set dummy environment variables before importing the app.

Ensures ``app.config`` can load in tests without a real ``.env`` file.
"""

import os

os.environ.setdefault("TWILIO_ACCOUNT_SID", "test_sid")
os.environ.setdefault("TWILIO_AUTH_TOKEN", "test_token")
os.environ.setdefault("TWILIO_PHONE_NUMBER", "+10000000000")
os.environ.setdefault("MY_PHONE_NUMBER", "+10000000001")
os.environ.setdefault("GMAIL_ADDRESS", "test.sender@gmail.com")
os.environ.setdefault("GMAIL_APP_PASSWORD", "test-app-password")
os.environ.setdefault("GMAIL_IMAP_HOST", "imap.gmail.com")
os.environ.setdefault("EMAIL_REPLY_POLL_MINUTES", "5")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("ALLOWED_EMAIL", "test@gmail.com")
