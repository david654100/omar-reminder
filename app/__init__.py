"""Omer Reminder — Flask application factory."""

import logging

from flask import Flask

from app import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def create_app() -> Flask:
    application = Flask(__name__)
    application.secret_key = config.SECRET_KEY

    from app import tracker
    tracker.init_db()

    from app.routes import bp
    application.register_blueprint(bp)

    return application
