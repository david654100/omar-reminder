"""Set dummy environment variables before any app imports."""

import os

os.environ.setdefault("TWILIO_ACCOUNT_SID", "test_sid")
os.environ.setdefault("TWILIO_AUTH_TOKEN", "test_token")
os.environ.setdefault("TWILIO_WHATSAPP_NUMBER", "whatsapp:+10000000000")
os.environ.setdefault("MY_PHONE_NUMBER", "whatsapp:+10000000001")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DASHBOARD_PASSWORD", "test-password")
