"""
Serialization package.

Responsible for converting internal application models into
JSON-serializable Python objects for API responses.

The serialization layer remains independent of both the
business logic and the Flask API.
"""

from .backtest_serializer import serialize_backtest_result
from .chart_serializer import build_charts
from .comparison_serializer import serialize_comparison_result

__all__ = [
    "serialize_backtest_result",
    "build_charts",
    "serialize_comparison_result",
]