"""Omer Reminder — Flask application factory."""

import logging

from authlib.integrations.flask_client import OAuth
from flask import Flask

from app import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

oauth = OAuth()


def create_app() -> Flask:
    application = Flask(__name__)
    application.secret_key = config.SECRET_KEY

    oauth.init_app(application)
    oauth.register(
        name="google",
        client_id=config.GOOGLE_CLIENT_ID,
        client_secret=config.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    from app import tracker
    tracker.init_db()

    from app.routes import bp
    application.register_blueprint(bp)

    return application
