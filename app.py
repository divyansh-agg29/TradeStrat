"""
Application entry point.
"""

from flask import Flask

from api import api
from utils.logger import get_logger

logger = get_logger(__name__)


def create_app() -> Flask:
    """
    Flask application factory.
    """

    app = Flask(__name__)

    # Register API blueprint
    app.register_blueprint(api)

    logger.info("Flask application initialized.")

    return app


app = create_app()


if __name__ == "__main__":
    logger.info("Starting Flask development server...")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )