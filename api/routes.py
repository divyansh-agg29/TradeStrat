"""
API routes.

All REST endpoints are defined here.
"""

from flask import jsonify, request, render_template, current_app


from api import api
from utils.logger import get_logger
from utils.rate_limiter import limiter

from models import BacktestRequest, ComparisonRequest, PositionSizingConfig, RiskConfig, StrategyConfig
from serialization import serialize_backtest_result, serialize_comparison_result
from services import run_backtest, run_comparison

logger = get_logger(__name__)

def _parse_comparison_request(data: dict) -> ComparisonRequest:
    """
    Parse raw JSON dict into a ComparisonRequest.

    Extracts common parameters (ticker, dates, capital, risk_free_rate, interval)
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
        interval=data.get("interval", "1d"),
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

    has_stop_loss = risk_data and risk_data.get("stop_loss_type")
    has_take_profit = risk_data and risk_data.get("take_profit_type")

    if has_stop_loss or has_take_profit:
        risk_config = RiskConfig(
            stop_loss_type=risk_data.get("stop_loss_type"),
            stop_loss_parameters=risk_data.get("parameters") or None,
            take_profit_type=risk_data.get("take_profit_type"),
            take_profit_parameters=risk_data.get("take_profit_parameters") or None,
        )

    sizing_data = data.get("position_sizing", {})
    position_sizing_config = None

    if sizing_data and sizing_data.get("sizing_type"):
        position_sizing_config = PositionSizingConfig(
            sizing_type=sizing_data.get("sizing_type"),
            sizing_parameters=sizing_data.get("parameters") or None,
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
        position_sizing=position_sizing_config,
        interval=data.get("interval", "1d"),
    )


@api.route("/", methods=["GET"])
def landing():
    """Landing page"""
    return render_template("landing.html")

@api.route("/app", methods=["GET"])
def dashboard():
    """Dashboard application"""
    return render_template("app.html")

@api.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    """

    return jsonify(
        {
            "success": True,
            "data": {
                "status": "healthy",
            },
        }
    ), 200

@api.route("/backtest", methods=["POST"])
@limiter.limit("5 per minute")
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

        db_path = current_app.config["DATABASE_PATH"]

        result = run_backtest(
            backtest_request,
            db_path=db_path,
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
@limiter.limit("5 per minute")
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

        db_path = current_app.config["DATABASE_PATH"]

        comparison_result = run_comparison(
            comparison_request,
            db_path=db_path,
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
