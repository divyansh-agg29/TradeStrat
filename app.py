"""
Application entry point.
"""
import os
import time
from flask import Flask, jsonify, request, g
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

    @app.before_request
    def log_request_start():
        """
        Record request start time and log the incoming request.
        """

        g.start_time = time.perf_counter()

        logger.info(
            "Request started: %s %s",
            request.method,
            request.path,
        )

    @app.after_request
    def log_request_end(response):
        """
        Log request completion and execution time.
        """

        duration = None

        if hasattr(g, "start_time"):
            duration = time.perf_counter() - g.start_time

        if duration is None:
            logger.info(
                "Request completed: %s %s | Status=%d",
                request.method,
                request.path,
                response.status_code,
            )
        else:
            logger.info(
                (
                    "Request completed: %s %s | "
                    "Status=%d | Duration=%.3fs"
                ),
                request.method,
                request.path,
                response.status_code,
                duration,
            )

        return response


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