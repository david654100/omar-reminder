import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_WHATSAPP_NUMBER = os.environ["TWILIO_WHATSAPP_NUMBER"]
MY_PHONE_NUMBER = os.environ["MY_PHONE_NUMBER"]

LATITUDE = float(os.getenv("LATITUDE", "44.9778"))
LONGITUDE = float(os.getenv("LONGITUDE", "-93.2650"))
TIMEZONE = os.getenv("TIMEZONE", "America/Chicago")
LOCATION_NAME = os.getenv("LOCATION_NAME", "Minneapolis")

MORNING_REMINDER_HOUR = int(os.getenv("MORNING_REMINDER_HOUR", "8"))

SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
DASHBOARD_PASSWORD = os.environ["DASHBOARD_PASSWORD"]
