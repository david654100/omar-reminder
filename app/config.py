import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_PHONE_NUMBER = os.environ["TWILIO_PHONE_NUMBER"]
MY_PHONE_NUMBER = os.environ["MY_PHONE_NUMBER"]

GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
GMAIL_IMAP_HOST = os.getenv("GMAIL_IMAP_HOST", "imap.gmail.com")
EMAIL_REPLY_POLL_MINUTES = int(os.getenv("EMAIL_REPLY_POLL_MINUTES", "5"))

LATITUDE = float(os.getenv("LATITUDE", "44.9778"))
LONGITUDE = float(os.getenv("LONGITUDE", "-93.2650"))
TIMEZONE = os.getenv("TIMEZONE", "America/Chicago")
LOCATION_NAME = os.getenv("LOCATION_NAME", "Minneapolis")

MORNING_REMINDER_HOUR = int(os.getenv("MORNING_REMINDER_HOUR", "8"))

SECRET_KEY = os.getenv("SECRET_KEY", "change-me")

GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
ALLOWED_EMAIL = os.environ["ALLOWED_EMAIL"]