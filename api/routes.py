"""
API routes.

All REST endpoints are defined here.
"""

from flask import jsonify

from api import api
from utils.logger import get_logger

logger = get_logger(__name__)


@api.route("/", methods=["GET"])
def health_check():
    """
    Health check endpoint.
    """

    logger.info("Health check endpoint accessed.")

    return jsonify(
        {
            "status": "running",
            "message": "Trading Strategy Analysis Platform API",
        }
    ), 200