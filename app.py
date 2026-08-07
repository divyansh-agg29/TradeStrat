"""
Application entry point.
"""
import os
from flask import Flask, jsonify
from flask_limiter.errors import RateLimitExceeded
from config import DevelopmentConfig, ProductionConfig

from api import api
from utils.logger import get_logger, configure_logging
from utils.rate_limiter import limiter


logger = get_logger(__name__)

def get_config():
    """
    Return the appropriate configuration class based on the environment.
    """
    environment = os.environ.get("APP_ENV", "development").lower()
    if environment == "production":
        return ProductionConfig
    return DevelopmentConfig


def create_app(config_object=None) -> Flask:
    """
    Flask application factory.

    config_object: The configuration class to use. (Allows tests to inject custom config)
    """

    app = Flask(
        __name__,
        template_folder="frontend/templates",
        static_folder="frontend/static"
    )

    if config_object is None:
        config_object = get_config()

    app.config.from_object(config_object)
    configure_logging(app.config["LOG_LEVEL"])

    limiter.init_app(app)

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit(error):
        """
        Return a standardized JSON response when
        the client exceeds the configured rate limit.
        """

        logger.warning(
            "Rate limit exceeded: %s",
            error.description,
        )

        return (
            jsonify(
                {
                    "success": False,
                    "error": {
                        "type": type(error).__name__,
                        "message": (
                            "Rate limit exceeded. "
                            f"Limit: {error.description}. "
                            "Please try again later."
                        ),
                    },
                }
            ),
            429,
        )

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