"""
Serialization package.

Responsible for converting internal application models into
JSON-serializable Python objects for API responses.

The serialization layer remains independent of both the
business logic and the Flask API.
"""

from .backtest_serializer import serialize_backtest_result

__all__ = [
    "serialize_backtest_result",
]