import pandas as pd
import pytest

from portfolio import SimulationResult, simulate_portfolio

def create_sample_dataframe(
    signals: list[str] | None = None,
    prices: list[float] | None = None,
) -> pd.DataFrame:
    """
    Create a sample DataFrame for portfolio simulator tests.

    Parameters
    ----------
    signals : list[str] | None
        Trading signals for each trading day.
        Defaults to all HOLD signals.

    prices : list[float] | None
        Closing prices for each trading day.
        Defaults to a small increasing price series.

    Returns
    -------
    pd.DataFrame
        Sample market data suitable for portfolio simulator tests.
    """

    if signals is None:
        signals = ["HOLD"] * 5

    if prices is None:
        prices = [100, 101, 102, 103, 104]

    if len(signals) != len(prices):
        raise ValueError(
            "signals and prices must have the same length."
        )

    dates = pd.date_range(
        start="2024-01-01",
        periods=len(prices),
        freq="D",
    )

    return pd.DataFrame(
        {
            "Close": prices,
            "Signal": signals,
        },
        index=dates,
    )


def test_invalid_dataframe():
    """
    Test that a TypeError is raised when the input is not a DataFrame.
    """

    with pytest.raises(
        TypeError,
        match="Input data must be a pandas DataFrame.",
    ):
        simulate_portfolio([])


def test_empty_dataframe():
    """
    Test that a ValueError is raised for an empty DataFrame.
    """

    df = pd.DataFrame()

    with pytest.raises(
        ValueError,
        match="Input DataFrame cannot be empty.",
    ):
        simulate_portfolio(df)


def test_missing_close_column():
    """
    Test that a ValueError is raised when the Close column is missing.
    """

    df = create_sample_dataframe()
    df = df.drop(columns=["Close"])

    with pytest.raises(
        ValueError,
        match="Missing required columns:",
    ):
        simulate_portfolio(df)


def test_missing_signal_column():
    """
    Test that a ValueError is raised when the Signal column is missing.
    """

    df = create_sample_dataframe()
    df = df.drop(columns=["Signal"])

    with pytest.raises(
        ValueError,
        match="Missing required columns:",
    ):
        simulate_portfolio(df)


def test_invalid_signal():
    """
    Test that a ValueError is raised for invalid trading signals.
    """

    df = create_sample_dataframe(
        signals=["BUY", "INVALID", "SELL", "HOLD", "BUY"]
    )

    with pytest.raises(
        ValueError,
        match="Invalid signal values found:",
    ):
        simulate_portfolio(df)


@pytest.mark.parametrize("initial_capital", [0, -100000])
def test_invalid_initial_capital(initial_capital):
    """
    Test that non-positive initial capital is rejected.
    """

    df = create_sample_dataframe()

    with pytest.raises(
        ValueError,
        match="Initial capital must be greater than zero.",
    ):
        simulate_portfolio(
            df,
            initial_capital=initial_capital,
        )

def test_buy_hold_sell_flow():
    """
    Test a complete BUY -> HOLD -> SELL trading flow.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD", "SELL"],
        prices=[100, 110, 120],
    )

    result = simulate_portfolio(df)

    portfolio = result.portfolio_history

    # Final portfolio state
    assert result.summary["position"] == "FLAT"
    assert result.summary["shares_held"] == 0
    assert result.summary["completed_trade_count"] == 1

    # Cash after selling should equal final portfolio value
    assert portfolio.iloc[-1]["Cash"] == portfolio.iloc[-1]["Portfolio Value"]

    # Position transitions
    assert portfolio.iloc[0]["Position"] == "LONG"
    assert portfolio.iloc[1]["Position"] == "LONG"
    assert portfolio.iloc[2]["Position"] == "FLAT"


def test_buy_ignored_when_already_long():
    """
    Test that BUY signals are ignored while already holding a position.
    """

    df = create_sample_dataframe(
        signals=["BUY", "BUY", "BUY"],
        prices=[100, 105, 110],
    )

    result = simulate_portfolio(df)

    portfolio = result.portfolio_history

    first_shares = portfolio.iloc[0]["Shares"]

    assert first_shares > 0

    # Shares should remain unchanged after ignored BUY signals.
    assert portfolio.iloc[1]["Shares"] == first_shares
    assert portfolio.iloc[2]["Shares"] == first_shares

    assert result.summary["completed_trade_count"] == 0
    assert result.summary["position"] == "LONG"


def test_sell_ignored_when_flat():
    """
    Test that SELL signals are ignored while no position is open.
    """

    df = create_sample_dataframe(
        signals=["SELL", "SELL", "SELL", "SELL", "SELL"],
    )

    result = simulate_portfolio(df)

    portfolio = result.portfolio_history

    assert (portfolio["Shares"] == 0).all()
    assert (portfolio["Position"] == "FLAT").all()

    assert result.trade_history.empty
    assert result.summary["completed_trade_count"] == 0


def test_hold_signal():
    """
    Test that HOLD signals do not change portfolio state.
    """

    df = create_sample_dataframe(
        signals=["HOLD"] * 5,
    )

    result = simulate_portfolio(df)

    portfolio = result.portfolio_history

    assert (portfolio["Cash"] == 100000).all()
    assert (portfolio["Shares"] == 0).all()
    assert (portfolio["Position"] == "FLAT").all()

    assert result.trade_history.empty


def test_buy_with_insufficient_cash():
    """
    Test that BUY is ignored when available cash is insufficient.
    """

    df = create_sample_dataframe(
        signals=["BUY"],
        prices=[200000],
    )

    result = simulate_portfolio(
        df,
        initial_capital=100000,
    )

    portfolio = result.portfolio_history

    assert portfolio.iloc[0]["Cash"] == 100000
    assert portfolio.iloc[0]["Shares"] == 0
    assert portfolio.iloc[0]["Position"] == "FLAT"

    assert result.trade_history.empty

def test_portfolio_value_updates():
    """
    Test that portfolio value is updated correctly throughout the simulation.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD", "SELL"],
        prices=[100, 110, 120],
    )

    result = simulate_portfolio(df)

    portfolio = result.portfolio_history

    # Buy day
    assert portfolio.iloc[0]["Portfolio Value"] == 100000

    # Holding day
    assert portfolio.iloc[1]["Portfolio Value"] == 110000

    # Sell day
    assert portfolio.iloc[2]["Portfolio Value"] == 120000


def test_cash_updates():
    """
    Test that cash balance is updated correctly after BUY and SELL.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD", "SELL"],
        prices=[100, 110, 120],
    )

    result = simulate_portfolio(df)

    portfolio = result.portfolio_history

    # Initial BUY
    assert portfolio.iloc[0]["Cash"] == 0

    # HOLD should not change cash
    assert portfolio.iloc[1]["Cash"] == 0

    # SELL converts holdings back to cash
    assert portfolio.iloc[2]["Cash"] == 120000


def test_shares_updates():
    """
    Test that the number of held shares is updated correctly.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD", "SELL"],
        prices=[100, 110, 120],
    )

    result = simulate_portfolio(df)

    portfolio = result.portfolio_history

    assert portfolio.iloc[0]["Shares"] == 1000
    assert portfolio.iloc[1]["Shares"] == 1000
    assert portfolio.iloc[2]["Shares"] == 0


def test_holdings_value_updates():
    """
    Test that holdings value is calculated correctly.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD", "SELL"],
        prices=[100, 110, 120],
    )

    result = simulate_portfolio(df)

    portfolio = result.portfolio_history

    assert portfolio.iloc[0]["Holdings Value"] == 100000
    assert portfolio.iloc[1]["Holdings Value"] == 110000
    assert portfolio.iloc[2]["Holdings Value"] == 0


def test_position_updates():
    """
    Test that portfolio position transitions correctly.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD", "SELL"],
        prices=[100, 110, 120],
    )

    result = simulate_portfolio(df)

    portfolio = result.portfolio_history

    assert portfolio.iloc[0]["Position"] == "LONG"
    assert portfolio.iloc[1]["Position"] == "LONG"
    assert portfolio.iloc[2]["Position"] == "FLAT"

def test_trade_history_created():
    """
    Test that a completed trade is recorded correctly.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD", "SELL"],
        prices=[100, 110, 120],
    )

    result = simulate_portfolio(df)

    trade_history = result.trade_history

    assert len(trade_history) == 1

    trade = trade_history.iloc[0]

    assert trade["entry_price"] == 100
    assert trade["exit_price"] == 120
    assert trade["shares"] == 1000


def test_open_trade_not_recorded():
    """
    Test that an open position at the end of the simulation
    is not included in trade history.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD", "HOLD"],
        prices=[100, 110, 120],
    )

    result = simulate_portfolio(df)

    assert result.trade_history.empty

    assert result.summary["position"] == "LONG"
    assert result.summary["open_position"] is True


def test_profit_calculation():
    """
    Test that profit/loss is calculated correctly.
    """

    df = create_sample_dataframe(
        signals=["BUY", "SELL"],
        prices=[100, 120],
    )

    result = simulate_portfolio(df)

    trade = result.trade_history.iloc[0]

    assert trade["investment"] == 100000
    assert trade["exit_value"] == 120000
    assert trade["profit_loss"] == 20000


def test_return_calculation():
    """
    Test that percentage return is calculated correctly.
    """

    df = create_sample_dataframe(
        signals=["BUY", "SELL"],
        prices=[100, 120],
    )

    result = simulate_portfolio(df)

    trade = result.trade_history.iloc[0]

    assert trade["return_pct"] == 20.0


def test_holding_period():
    """
    Test that holding period is measured in trading periods.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD", "HOLD", "SELL"],
        prices=[100, 105, 110, 120],
    )

    result = simulate_portfolio(df)

    trade = result.trade_history.iloc[0]

    assert trade["holding_period"] == 3


def test_multiple_completed_trades():
    """
    Test that multiple completed trades are recorded correctly.
    """

    df = create_sample_dataframe(
        signals=[
            "BUY",
            "SELL",
            "BUY",
            "SELL",
        ],
        prices=[
            100,
            110,
            100,
            120,
        ],
    )

    result = simulate_portfolio(df)

    trade_history = result.trade_history

    assert len(trade_history) == 2

def test_summary_generation():
    """
    Test that the simulation summary is generated correctly.
    """

    df = create_sample_dataframe(
        signals=["BUY", "SELL"],
        prices=[100, 120],
    )

    result = simulate_portfolio(df)

    summary = result.summary

    assert summary["initial_capital"] == 100000
    assert summary["final_portfolio_value"] == 120000
    assert summary["cash"] == 120000
    assert summary["shares_held"] == 0
    assert summary["position"] == "FLAT"
    assert summary["open_position"] is False
    assert summary["completed_trade_count"] == 1


def test_summary_with_open_position():
    """
    Test summary generation when the simulation ends
    with an open position.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD"],
        prices=[100, 120],
    )

    result = simulate_portfolio(df)

    summary = result.summary

    assert summary["initial_capital"] == 100000
    assert summary["final_portfolio_value"] == 120000
    assert summary["cash"] == 0
    assert summary["shares_held"] == 1000
    assert summary["position"] == "LONG"
    assert summary["open_position"] is True
    assert summary["completed_trade_count"] == 0

def test_return_type():
    """
    Test that simulate_portfolio returns a SimulationResult.
    """

    df = create_sample_dataframe()

    result = simulate_portfolio(df)

    assert isinstance(result, SimulationResult)