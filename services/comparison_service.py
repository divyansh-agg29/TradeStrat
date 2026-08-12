"""
Comparison Service

This module orchestrates the strategy comparison workflow.

It accepts a ComparisonRequest, runs each strategy sequentially
via the existing run_backtest function, and returns a ComparisonResult.

Each strategy executes in its own try/except so that one failure
does not block the remaining strategies.
"""

import logging
from models import (
    BacktestRequest,
    StrategyConfig,
    ComparisonRequest,
    ComparisonResult,
    StrategyResult,
)
from services.backtest_service import run_backtest
from utils.logger import get_logger

logger = get_logger(__name__)


def run_comparison(
    request: ComparisonRequest,
    db_path: str,
) -> ComparisonResult:
    """
    Execute a strategy comparison.

    Parameters
    ----------
    request : ComparisonRequest
        Comparison configuration containing shared parameters
        and a list of 2-6 strategy configurations.
    db_path : str
        Path to the SQLite database file for market data storage.

    Returns
    -------
    ComparisonResult
        Aggregated result containing per-strategy outcomes.

    Raises
    ------
    ValueError
        If the number of strategies is not between 2 and 6.
    """

    strategy_count = len(request.strategies)
    if strategy_count < 2 or strategy_count > 6:
        raise ValueError(
            "A comparison requires between 2 and 6 strategies."
        )

    logger.info(
        "Starting comparison with %d strategies for %s (interval=%s).",
        strategy_count,
        request.ticker,
        request.interval,
    )

    strategy_results: list[StrategyResult] = []

    for i, strategy_config in enumerate(request.strategies, start=1):
        backtest_request = BacktestRequest(
            ticker=request.ticker,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            risk_free_rate=request.risk_free_rate,
            strategy=strategy_config,
            interval=request.interval,
        )

        try:
            logger.info(
                "Running strategy %d/%d: %s",
                i,
                strategy_count,
                strategy_config.type,
            )
            result = run_backtest(backtest_request, db_path)
            strategy_results.append(
                StrategyResult(
                    strategy=strategy_config,
                    success=True,
                    backtest_result=result,
                )
            )
        except Exception as exc:
            logger.warning(
                "Strategy %d/%d (%s) failed: %s",
                i,
                strategy_count,
                strategy_config.type,
                str(exc),
            )
            strategy_results.append(
                StrategyResult(
                    strategy=strategy_config,
                    success=False,
                    error=str(exc),
                )
            )

    logger.info("Comparison completed.")

    return ComparisonResult(
        request=request,
        strategy_results=strategy_results,
    )
