"""
API routes.

All REST endpoints are defined here.
"""

from flask import jsonify, request, render_template


from api import api
from utils.logger import get_logger

from models import BacktestRequest, ComparisonRequest, RiskConfig, StrategyConfig
from serialization import serialize_backtest_result, serialize_comparison_result
from services import run_backtest, run_comparison

logger = get_logger(__name__)

def _parse_comparison_request(data: dict) -> ComparisonRequest:
    """
    Parse raw JSON dict into a ComparisonRequest.

    Extracts common parameters (ticker, dates, capital, risk_free_rate)
    and builds a list of StrategyConfig objects from the strategies array.
    """

    strategies_raw = data.get("strategies", [])

    strategies = [
        StrategyConfig(
            type=s.get("type", ""),
            parameters=s.get("parameters", {}),
        )
        for s in strategies_raw
    ]

    return ComparisonRequest(
        ticker=data.get("ticker", ""),
        start_date=data.get("start_date", ""),
        end_date=data.get("end_date", ""),
        initial_capital=float(data.get("initial_capital", 100000)),
        risk_free_rate=float(data.get("risk_free_rate", 0.0)),
        strategies=strategies,
    )


def _parse_request(data: dict) -> BacktestRequest:
    """
    Parse the incoming HTTP request into a BacktestRequest.
    """

    strategy = data.get("strategy")

    if strategy is None:
        raise ValueError(
            "Missing required field: strategy."
        )

    strategy_config = StrategyConfig(
        type=strategy.get("type", ""),
        parameters=strategy.get("parameters", {}),
    )

    risk_data = data.get("risk", {})
    risk_config = None

    if risk_data and risk_data.get("stop_loss_type"):
        risk_config = RiskConfig(
            stop_loss_type=risk_data["stop_loss_type"],
            stop_loss_parameters=risk_data.get("parameters", {}),
        )

    return BacktestRequest(
        ticker=data.get("ticker", ""),
        start_date=data.get("start_date", ""),
        end_date=data.get("end_date", ""),
        initial_capital=data.get(
            "initial_capital",
            100000,
        ),
        risk_free_rate=data.get(
            "risk_free_rate",
            0.0,
        ),
        strategy=strategy_config,
        risk=risk_config,
    )


@api.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@api.route("/backtest", methods=["POST"])
def backtest():
    """
    Execute a complete strategy backtest.
    """

    logger.info("Backtest request received.")

    try:

        data = request.get_json(silent=True)

        if data is None:
            raise ValueError(
                "Request body must contain valid JSON."
            )

        backtest_request = _parse_request(data)

        result = run_backtest(
            backtest_request
        )

        response = serialize_backtest_result(
            result
        )

        logger.info(
            "Backtest completed successfully."
        )

        return jsonify(
            {
                "success": True,
                "data": response,
            }
        ), 200

    except ValueError as exc:

        logger.warning(str(exc))

        return jsonify(
            {
                "success": False,
                "error": {
                    "type": type(exc).__name__,
                    "message": str(exc),
                },
            }
        ), 400

    except Exception as exc:

        logger.exception(
            "Unexpected error while executing backtest."
        )

        return jsonify(
            {
                "success": False,
                "error": {
                    "type": type(exc).__name__,
                    "message": "An unexpected internal error occurred.",
                },
            }
        ), 500


@api.route("/compare", methods=["POST"])
def compare():
    """
    Execute a strategy comparison.
    Accepts 2–6 strategy configurations with shared common parameters.
    """

    logger.info("Comparison request received.")

    try:

        data = request.get_json(silent=True)

        if data is None:
            raise ValueError(
                "Request body must contain valid JSON."
            )

        comparison_request = _parse_comparison_request(data)

        comparison_result = run_comparison(
            comparison_request
        )

        response = serialize_comparison_result(
            comparison_result
        )

        logger.info(
            "Comparison completed successfully."
        )

        return jsonify(
            {
                "success": True,
                "data": response,
            }
        ), 200

    except (ValueError, KeyError) as exc:

        logger.warning(str(exc))

        return jsonify(
            {
                "success": False,
                "error": {
                    "type": type(exc).__name__,
                    "message": str(exc),
                },
            }
        ), 400

    except Exception as exc:

        logger.exception(
            "Unexpected error while executing comparison."
        )

        return jsonify(
            {
                "success": False,
                "error": {
                    "type": type(exc).__name__,
                    "message": "An unexpected internal error occurred.",
                },
            }
        ), 500
