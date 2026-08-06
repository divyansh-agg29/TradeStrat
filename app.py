"""
Application entry point.
"""
import os
from flask import Flask
from config import DevelopmentConfig, ProductionConfig

from api import api
from utils.logger import get_logger, configure_logging


logger = get_logger(__name__)

def get_config():
    """
    Return the appropriate configuration class based on the environment.
    """

    environment = os.environ.get("APP_ENV", "development").lower()

    if environment == "production":
        return ProductionConfig

    return DevelopmentConfig


def create_app() -> Flask:
    """
    Flask application factory.
    """

    app = Flask(
        __name__,
        template_folder="frontend/templates",
        static_folder="frontend/static"
    )

    app.config.from_object(get_config())
    configure_logging(app.config["LOG_LEVEL"])

    app.register_blueprint(api)

    logger.info("Flask application initialized.")

    return app


app = create_app()


if __name__ == "__main__":
    logger.info("Starting Flask development server...")

    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"],
    )