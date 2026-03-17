# Omer Reminder

A WhatsApp bot that sends you a nightly reminder to count Sefirat HaOmer at **tzet hakochavim** (nightfall), calculated for Minneapolis. Includes the full bracha and count text in Hebrew with transliteration.

## Features

- Sends WhatsApp reminder at the exact tzet hakochavim time each night
- Includes the bracha and count in Hebrew + transliteration
- Skips Shabbat and Yom Tov
- Morning follow-up (without bracha) if you missed the night before
- Reply "YES" to confirm you counted
- Reply "STATUS" for a summary of your counting history
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
    ├── messaging.py      # Twilio WhatsApp send logic
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
2. Go to **Messaging > Try it out > Send a WhatsApp message** to activate the sandbox
3. Follow the instructions to join the sandbox from your phone
4. Note your **Account SID**, **Auth Token**, and sandbox WhatsApp number

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your Twilio credentials and phone number.

### 3. Install & Run

```bash
pip install -r requirements.txt
python run.py
```

The app runs on `http://localhost:5000`. The dashboard is at `/` and the Twilio webhook is at `/webhook`.

### 4. Configure Twilio Webhook

Set your Twilio WhatsApp sandbox webhook URL to:

```
https://your-server.com/webhook
```

For local development, use [ngrok](https://ngrok.com):

```bash
ngrok http 5000
```

Then paste the ngrok URL + `/webhook` into the Twilio sandbox settings.

### 5. Deploy (Optional)

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
2. **At tzet hakochavim** — sends WhatsApp with bracha + count (unless Shabbat/Yom Tov)
3. **8:00 AM next day** — if you didn't reply YES, sends a follow-up without the bracha
4. **You reply YES** — recorded in the database, streak updated
5. **You reply STATUS** — get a text summary of your counting history
6. **Visit the dashboard** — see a visual 7x7 grid of your Omer counting progress
