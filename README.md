# Omer Reminder

Sends you nightly SMS and email reminders to count Sefirat HaOmer at **tzet hakochavim** (nightfall), calculated for Minneapolis. Includes the full bracha and count text in Hebrew with transliteration.

## Features

- Sends SMS + email reminders at the exact tzet hakochavim time each night
- Includes the bracha and count in Hebrew + transliteration
- Skips Shabbat and Yom Tov
- Morning follow-up (without bracha) if you missed the night before
- Reply "YES" by SMS or email to confirm you counted
- Reply "STATUS" by SMS or email for a summary of your counting history
- Web dashboard with a 7x7 Omer grid, streak tracker, and history

## Project Structure

```
├── .env.example          # Template for environment variables
├── .gitignore
├── Dockerfile
├── README.md
├── requirements.txt
├── run.py                # Development entry point
├── wsgi.py               # Production entry point (gunicorn)
│
└── app/
    ├── __init__.py       # Flask app factory
    ├── config.py         # Loads settings from .env
    ├── messaging.py      # Twilio SMS + Gmail email send logic
    ├── omer.py           # Counting text: bracha, Hebrew, transliteration
    ├── routes.py         # Flask routes: /webhook and / (dashboard)
    ├── scheduler.py      # APScheduler: evening + morning reminder jobs
    ├── tracker.py        # SQLite database for recording counts
    ├── zmanim.py         # Tzet hakochavim + Shabbat/Yom Tov detection
    └── templates/
        └── dashboard.html
│
└── tests/
    ├── test_omer.py      # Omer day calculation and message formatting
    ├── test_zmanim.py    # Zmanim calculation and holiday detection
    ├── test_tracker.py   # SQLite tracker database
    └── test_routes.py    # Flask webhook and dashboard routes
```

## Setup

### 1. Twilio Account

1. Sign up at [twilio.com](https://www.twilio.com)
2. Buy an SMS-capable phone number (Phone Numbers > Buy a Number)
3. Note your **Account SID**, **Auth Token**, and the phone number you purchased

### 2. Gmail App Password

1. Use a Gmail account for sending notifications.
2. Enable 2-Step Verification on that account.
3. Generate an app password at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).
4. Copy the generated 16-character password.
5. Ensure IMAP is enabled in your Gmail settings (for reading email replies).

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your Twilio credentials, phone numbers, Gmail sender credentials, and Google OAuth values.

Email notifications are sent only to `ALLOWED_EMAIL`.
Email replies are also polled from that same inbox.

### 4. Install & Run

```bash
pip install -r requirements.txt
python run.py
```

The app runs on `http://localhost:5000`. The dashboard is at `/` and the Twilio webhook is at `/webhook`.

### 5. Configure Twilio Webhook (for SMS replies)

Set your Twilio phone number's **Messaging webhook URL** to:

```
https://your-server.com/webhook
```

You can configure this in the Twilio Console under Phone Numbers > Active Numbers > your number > Messaging.

For local development, use [ngrok](https://ngrok.com):

```bash
ngrok http 5000
```

Then paste the ngrok URL + `/webhook` into your Twilio number's messaging settings.

### 6. Deploy (Optional)

Build and run with Docker:

```bash
docker build -t omer-reminder .
docker run -d --env-file .env -p 5000:5000 omer-reminder
```

Or deploy to Render/Railway by connecting your GitHub repo.

## Running Tests

```bash
pytest
```

Tests cover Omer day calculations, Hebrew/transliteration output for all 49 days, Shabbat and Yom Tov detection, the SQLite tracker, and the Flask webhook and dashboard routes.

## How It Works

1. **3:00 PM daily** — calculates tonight's tzet hakochavim for Minneapolis
2. **At tzet hakochavim** — sends SMS + email with bracha + count (unless Shabbat/Yom Tov)
3. **8:00 AM next day** — if you didn't reply YES, sends a follow-up without the bracha
4. **You reply YES via SMS** — recorded in the database, streak updated
5. **You reply STATUS via SMS or email** — get a summary of your counting history
6. **Visit the dashboard** — see a visual 7x7 grid of your Omer counting progress
