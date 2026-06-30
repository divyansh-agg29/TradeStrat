"""
API package.

Defines the application's main Blueprint.
"""

from flask import Blueprint

api = Blueprint("api", __name__)

# Import routes after creating the blueprint to avoid circular imports.
from api import routes