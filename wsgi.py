"""Production entry point for gunicorn."""

from app import create_app
from app import scheduler

app = create_app()
scheduler.start()
