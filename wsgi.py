"""WSGI entry point for production servers (e.g. gunicorn).

Usage example: ``gunicorn wsgi:app``
"""

from app import create_app
from app import scheduler

app = create_app()
scheduler.start()
