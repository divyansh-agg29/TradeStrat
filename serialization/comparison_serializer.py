"""
Comparison Serializer

Converts a ComparisonResult into a JSON-serializable dictionary
for the /compare API response.

Reuses serialize_backtest_result per strategy, then applies
post-processing to strip kpi_cards and benchmark_metrics
(which are single-backtest UI concepts not needed in the
comparison context).
"""

from models import ComparisonResult
from serialization.backtest_serializer import serialize_backtest_result
from utils.logger import get_logger

logger = get_logger(__name__)

_NULL_RESULT_FIELDS = {
    "portfolio_metrics": None,
    "risk_metrics": None,
    "trade_metrics": None,
    "portfolio_history": None,
    "analytics_history": None,
    "trade_history": None,
}


def serialize_comparison_result(result: ComparisonResult) -> dict:
    """
    Convert a ComparisonResult into a JSON-serializable dictionary.

    Parameters
    ----------
    result : ComparisonResult
        Completed comparison result.

    Returns
    -------
    dict
        JSON-serializable representation of the comparison.
    """

    logger.info("Serializing comparison result.")

    common = {
        "ticker": result.request.ticker,
        "start_date": result.request.start_date,
        "end_date": result.request.end_date,
        "initial_capital": result.request.initial_capital,
        "risk_free_rate": result.request.risk_free_rate,
    }

    benchmark = _extract_benchmark(result)

    results = []
    for strategy_result in result.strategy_results:
        strategy_echo = {
            "type": strategy_result.strategy.type,
            "parameters": strategy_result.strategy.parameters,
        }

        if strategy_result.success:
            serialized = serialize_backtest_result(
                strategy_result.backtest_result
            )
            serialized.pop("kpi_cards", None)
            serialized.pop("benchmark_metrics", None)
            serialized["strategy"] = strategy_echo
            serialized["success"] = True
            serialized["error"] = None
            results.append(serialized)
        else:
            entry = {
                "strategy": strategy_echo,
                "success": False,
                "error": strategy_result.error,
                **_NULL_RESULT_FIELDS,
            }
            results.append(entry)

    return {
        "common": common,
        "benchmark": benchmark,
        "results": results,
    }


def _extract_benchmark(result: ComparisonResult):
    """
    Extract benchmark data from the first successful strategy.

    Returns None if no strategies succeeded.
    """

    for strategy_result in result.strategy_results:
        if strategy_result.success:
            serialized = serialize_backtest_result(
                strategy_result.backtest_result
            )

            benchmark_metrics = serialized.get("benchmark_metrics")

            analytics_history = serialized.get("analytics_history", [])
            portfolio_history = [
                {
                    "Date": record.get("Date"),
                    "Buy & Hold Value": record.get("Buy & Hold Value"),
                }
                for record in analytics_history
            ]

            return {
                "portfolio_history": portfolio_history,
                "benchmark_metrics": benchmark_metrics,
            }

    return None
