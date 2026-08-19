import pandas as pd
import pytest

from portfolio import SimulationResult, simulate_portfolio, PositionEntry, OpenPosition
from portfolio.simulator import CompletedTrade, PortfolioState
from position_sizing.config import PositionSizingConfig
from risk.config import RiskConfig

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


def test_stop_loss_uses_configured_percentage():
    """
    Test that the stop-loss threshold comes from the supplied risk config.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD", "HOLD"],
        prices=[100, 96.5, 96.5],
    )

    risk_config = RiskConfig(
        stop_loss_type="fixed_percentage",
        stop_loss_parameters={"percent": 0.05},
    )

    result = simulate_portfolio(
        df,
        risk_config=risk_config,
    )

    assert result.trade_history.empty
    assert result.summary["completed_trade_count"] == 0
    assert result.summary["position"] == "LONG"


def test_stop_loss_closes_trade_and_updates_portfolio_state():
    """
    Test that a configured stop loss closes the trade and updates cash.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD", "HOLD"],
        prices=[100, 94, 110],
    )

    result = simulate_portfolio(
        df,
        risk_config=RiskConfig(
            stop_loss_type="fixed_percentage",
            stop_loss_parameters={"percent": 0.05},
        ),
    )

    portfolio = result.portfolio_history

    assert result.summary["position"] == "FLAT"
    assert result.summary["shares_held"] == 0
    assert result.summary["cash"] == 94000
    assert result.summary["final_portfolio_value"] == 94000
    assert result.summary["completed_trade_count"] == 1

    assert portfolio.iloc[1]["Cash"] == 94000
    assert portfolio.iloc[1]["Shares"] == 0
    assert portfolio.iloc[1]["Holdings Value"] == 0
    assert portfolio.iloc[1]["Portfolio Value"] == 94000
    assert portfolio.iloc[1]["Position"] == "FLAT"


def test_stop_loss_trade_history_records_exit_reason():
    """
    Test that stop-loss exits are identifiable in trade history.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD"],
        prices=[100, 95],
    )

    result = simulate_portfolio(
        df,
        risk_config=RiskConfig(
            stop_loss_type="fixed_percentage",
            stop_loss_parameters={"percent": 0.05},
        ),
    )

    trade = result.trade_history.iloc[0]

    assert trade["entry_price"] == 100
    assert trade["exit_price"] == 95
    assert trade["shares"] == 1000
    assert trade["investment"] == 100000
    assert trade["exit_value"] == 95000
    assert trade["profit_loss"] == -5000
    assert trade["return_pct"] == -5.0
    assert trade["holding_period"] == 1
    assert trade["exit_reason"] == "stop_loss"
    assert trade["stop_loss_price"] == 95


def test_default_mode_ignores_stop_loss_threshold():
    """
    Test that no stop loss is applied when no risk settings are supplied.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD", "SELL"],
        prices=[100, 94, 110],
    )

    result = simulate_portfolio(df)

    trade = result.trade_history.iloc[0]

    assert result.summary["final_portfolio_value"] == 110000
    assert result.summary["completed_trade_count"] == 1
    assert trade["exit_price"] == 110
    assert trade["exit_reason"] == "signal"
    assert trade["stop_loss_price"] is None


def test_signal_based_exit_still_occurs_with_risk_config():
    """
    Test that normal SELL exits still work when stop loss is not reached.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD", "SELL"],
        prices=[100, 101, 103],
    )

    result = simulate_portfolio(
        df,
        risk_config=RiskConfig(
            stop_loss_type="fixed_percentage",
            stop_loss_parameters={"percent": 0.05},
        ),
    )

    trade = result.trade_history.iloc[0]

    assert result.summary["final_portfolio_value"] == 103000
    assert result.summary["completed_trade_count"] == 1
    assert trade["exit_price"] == 103
    assert trade["exit_reason"] == "signal"
    assert trade["stop_loss_price"] is None


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


def test_fixed_price_offset_stop_loss_closes_trade():
    """
    Test that a fixed price offset stop-loss closes the trade correctly.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD", "HOLD"],
        prices=[500, 449, 460],
    )

    result = simulate_portfolio(
        df,
        risk_config=RiskConfig(
            stop_loss_type="fixed_price_offset",
            stop_loss_parameters={"offset": 50},
        ),
    )

    assert result.summary["position"] == "FLAT"
    assert result.summary["completed_trade_count"] == 1
    assert result.summary["shares_held"] == 0


def test_fixed_price_offset_stop_loss_records_exit_details():
    """
    Test that fixed price offset stop-loss exits are recorded in trade history.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD"],
        prices=[500, 440],
    )

    result = simulate_portfolio(
        df,
        risk_config=RiskConfig(
            stop_loss_type="fixed_price_offset",
            stop_loss_parameters={"offset": 50},
        ),
    )

    trade = result.trade_history.iloc[0]

    assert trade["entry_price"] == 500
    assert trade["exit_price"] == 440
    assert trade["exit_reason"] == "stop_loss"
    assert trade["stop_loss_price"] == 450


def test_trailing_stop_loss_closes_trade():
    """
    Test that a trailing stop-loss closes the trade after price rises and then falls.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD", "HOLD", "HOLD"],
        prices=[100, 120, 110, 108],
    )

    result = simulate_portfolio(
        df,
        risk_config=RiskConfig(
            stop_loss_type="trailing_stop",
            stop_loss_parameters={"percent": 0.10},
        ),
    )

    assert result.summary["position"] == "FLAT"
    assert result.summary["completed_trade_count"] == 1
    assert result.summary["shares_held"] == 0


def test_trailing_stop_loss_records_exit_details():
    """
    Test that trailing stop-loss exits are recorded in trade history using peak price.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD", "HOLD"],
        prices=[100, 120, 108],
    )

    result = simulate_portfolio(
        df,
        risk_config=RiskConfig(
            stop_loss_type="trailing_stop",
            stop_loss_parameters={"percent": 0.10},
        ),
    )

    trade = result.trade_history.iloc[0]

    assert trade["entry_price"] == 100
    assert trade["exit_price"] == 108
    assert trade["exit_reason"] == "stop_loss"
    assert trade["stop_loss_price"] == 108


def test_take_profit_closes_trade():
    """
    Test that a take-profit closes the trade when price reaches the target.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD", "HOLD"],
        prices=[100, 110, 120],
    )

    result = simulate_portfolio(
        df,
        risk_config=RiskConfig(
            take_profit_type="fixed_percentage",
            take_profit_parameters={"percent": 0.20},
        ),
    )

    assert result.summary["position"] == "FLAT"
    assert result.summary["completed_trade_count"] == 1
    assert result.summary["shares_held"] == 0


def test_take_profit_records_exit_details():
    """
    Test that take-profit exits are recorded in trade history.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD"],
        prices=[100, 120],
    )

    result = simulate_portfolio(
        df,
        risk_config=RiskConfig(
            take_profit_type="fixed_percentage",
            take_profit_parameters={"percent": 0.20},
        ),
    )

    trade = result.trade_history.iloc[0]

    assert trade["entry_price"] == 100
    assert trade["exit_price"] == 120
    assert trade["exit_reason"] == "take_profit"
    assert trade["take_profit_price"] == 120


def test_stop_loss_takes_priority_over_take_profit():
    """
    When both stop-loss and take-profit are configured,
    stop-loss should be evaluated first.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD"],
        prices=[100, 80],
    )

    result = simulate_portfolio(
        df,
        risk_config=RiskConfig(
            stop_loss_type="fixed_percentage",
            stop_loss_parameters={"percent": 0.10},
            take_profit_type="fixed_percentage",
            take_profit_parameters={"percent": 0.20},
        ),
    )

    trade = result.trade_history.iloc[0]

    assert trade["exit_reason"] == "stop_loss"


# ── PortfolioState (position removed) ───────────────────────


def test_portfolio_state_has_no_position_field():
    """
    PortfolioState should no longer have a 'position' field.
    """

    state = PortfolioState(cash=100000, shares=0)

    assert not hasattr(state, "position")
    assert state.cash == 100000
    assert state.shares == 0


def test_portfolio_state_position_derived_from_shares():
    """
    Position should be derivable from shares > 0.
    """

    flat = PortfolioState(cash=100000, shares=0)
    long = PortfolioState(cash=50000, shares=500)

    assert flat.shares == 0  # FLAT
    assert long.shares > 0   # LONG


# ── PositionEntry ────────────────────────────────────────────


def test_position_entry_creation():
    """
    PositionEntry should store all entry details.
    """

    entry = PositionEntry(
        entry_date=pd.Timestamp("2024-01-01"),
        entry_index=0,
        entry_price=100.0,
        shares=500,
        investment=50000.0,
    )

    assert entry.entry_date == pd.Timestamp("2024-01-01")
    assert entry.entry_index == 0
    assert entry.entry_price == 100.0
    assert entry.shares == 500
    assert entry.investment == 50000.0


# ── OpenPosition ─────────────────────────────────────────────


def test_open_position_single_entry():
    """
    OpenPosition with a single entry should have correct aggregated fields.
    """

    entry = PositionEntry(
        entry_date=pd.Timestamp("2024-01-01"),
        entry_index=0,
        entry_price=100.0,
        shares=500,
        investment=50000.0,
    )

    position = OpenPosition(
        entries=[entry],
        total_shares=500,
        total_investment=50000.0,
        average_entry_price=100.0,
        highest_close=100.0,
    )

    assert position.total_shares == 500
    assert position.total_investment == 50000.0
    assert position.average_entry_price == 100.0
    assert position.highest_close == 100.0
    assert len(position.entries) == 1


def test_open_position_add_entry():
    """
    Adding an entry should recalculate weighted average and totals.

    Entry 1: 100 shares @ $50 = $5,000
    Entry 2: 100 shares @ $60 = $6,000
    Total: 200 shares, $11,000 invested, avg price $55
    """

    entry = PositionEntry(
        entry_date=pd.Timestamp("2024-01-01"),
        entry_index=0,
        entry_price=50.0,
        shares=100,
        investment=5000.0,
    )

    position = OpenPosition(
        entries=[entry],
        total_shares=100,
        total_investment=5000.0,
        average_entry_price=50.0,
        highest_close=55.0,
    )

    position.add_entry(
        entry_date=pd.Timestamp("2024-01-05"),
        entry_index=4,
        entry_price=60.0,
        shares=100,
    )

    assert position.total_shares == 200
    assert position.total_investment == 11000.0
    assert position.average_entry_price == 55.0
    assert len(position.entries) == 2

    second = position.entries[1]
    assert second.entry_price == 60.0
    assert second.shares == 100
    assert second.investment == 6000.0


def test_open_position_add_multiple_entries():
    """
    Adding multiple entries should track weighted average correctly.

    Entry 1: 200 shares @ $100 = $20,000
    Entry 2: 100 shares @ $110 = $11,000
    Entry 3: 300 shares @ $90  = $27,000
    Total: 600 shares, $58,000 invested, avg price $96.67
    """

    entry = PositionEntry(
        entry_date=pd.Timestamp("2024-01-01"),
        entry_index=0,
        entry_price=100.0,
        shares=200,
        investment=20000.0,
    )

    position = OpenPosition(
        entries=[entry],
        total_shares=200,
        total_investment=20000.0,
        average_entry_price=100.0,
        highest_close=105.0,
    )

    position.add_entry(
        entry_date=pd.Timestamp("2024-01-10"),
        entry_index=9,
        entry_price=110.0,
        shares=100,
    )

    position.add_entry(
        entry_date=pd.Timestamp("2024-01-20"),
        entry_index=19,
        entry_price=90.0,
        shares=300,
    )

    assert position.total_shares == 600
    assert position.total_investment == 58000.0
    assert position.average_entry_price == pytest.approx(
        96.6667, rel=1e-3
    )
    assert len(position.entries) == 3


def test_open_position_highest_close_preserved():
    """
    Adding entries should not affect highest_close (that is
    updated by the simulation loop, not by add_entry).
    """

    entry = PositionEntry(
        entry_date=pd.Timestamp("2024-01-01"),
        entry_index=0,
        entry_price=100.0,
        shares=100,
        investment=10000.0,
    )

    position = OpenPosition(
        entries=[entry],
        total_shares=100,
        total_investment=10000.0,
        average_entry_price=100.0,
        highest_close=115.0,
    )

    position.add_entry(
        entry_date=pd.Timestamp("2024-01-10"),
        entry_index=9,
        entry_price=105.0,
        shares=50,
    )

    assert position.highest_close == 115.0


# ── CompletedTrade new fields ────────────────────────────────


def test_completed_trade_default_num_entries():
    """
    CompletedTrade should default to num_entries=1 for backward
    compatibility.
    """

    trade = CompletedTrade(
        entry_date=pd.Timestamp("2024-01-01"),
        exit_date=pd.Timestamp("2024-01-10"),
        entry_price=100.0,
        exit_price=120.0,
        shares=1000,
        investment=100000.0,
        exit_value=120000.0,
        profit_loss=20000.0,
        return_pct=20.0,
        holding_period=9,
    )

    assert trade.num_entries == 1
    assert trade.first_entry_date is None


def test_completed_trade_with_multiple_entries():
    """
    CompletedTrade should accept explicit num_entries and first_entry_date.
    """

    trade = CompletedTrade(
        entry_date=pd.Timestamp("2024-01-05"),
        exit_date=pd.Timestamp("2024-01-20"),
        entry_price=55.0,
        exit_price=65.0,
        shares=200,
        investment=11000.0,
        exit_value=13000.0,
        profit_loss=2000.0,
        return_pct=18.18,
        holding_period=15,
        num_entries=2,
        first_entry_date=pd.Timestamp("2024-01-01"),
    )

    assert trade.num_entries == 2
    assert trade.first_entry_date == pd.Timestamp("2024-01-01")


# ── Position Sizing Integration ──────────────────────────────


def test_fixed_percentage_sizing_limits_buy():
    """
    With 25% sizing, only 25% of portfolio value should be invested.
    $100k * 25% = $25k allocation -> 250 shares at $100.
    """

    df = create_sample_dataframe(
        signals=["BUY", "HOLD", "SELL"],
        prices=[100, 110, 120],
    )

    sizing = PositionSizingConfig(
        sizing_type="fixed_percentage",
        sizing_parameters={"percent": 0.25},
    )

    result = simulate_portfolio(
        df,
        position_sizing_config=sizing,
    )

    portfolio = result.portfolio_history

    assert portfolio.iloc[0]["Shares"] == 250
    assert portfolio.iloc[0]["Cash"] == 75000

    trade = result.trade_history.iloc[0]
    assert trade["shares"] == 250
    assert trade["investment"] == 25000
    assert trade["exit_value"] == 30000
    assert trade["profit_loss"] == 5000


def test_fixed_amount_sizing():
    """
    With $10k fixed amount, should buy $10k worth of shares.
    $10k / $100 = 100 shares.
    """

    df = create_sample_dataframe(
        signals=["BUY", "SELL"],
        prices=[100, 120],
    )

    sizing = PositionSizingConfig(
        sizing_type="fixed_amount",
        sizing_parameters={"amount": 10000},
    )

    result = simulate_portfolio(
        df,
        position_sizing_config=sizing,
    )

    portfolio = result.portfolio_history

    assert portfolio.iloc[0]["Shares"] == 100
    assert portfolio.iloc[0]["Cash"] == 90000


def test_fixed_shares_sizing():
    """
    With 200 fixed shares, should buy exactly 200 shares.
    """

    df = create_sample_dataframe(
        signals=["BUY", "SELL"],
        prices=[100, 120],
    )

    sizing = PositionSizingConfig(
        sizing_type="fixed_shares",
        sizing_parameters={"shares": 200},
    )

    result = simulate_portfolio(
        df,
        position_sizing_config=sizing,
    )

    portfolio = result.portfolio_history

    assert portfolio.iloc[0]["Shares"] == 200
    assert portfolio.iloc[0]["Cash"] == 80000


def test_no_sizing_config_defaults_to_all_in():
    """
    Without position_sizing_config, should use all cash (backward compat).
    """

    df = create_sample_dataframe(
        signals=["BUY", "SELL"],
        prices=[100, 120],
    )

    result = simulate_portfolio(df)

    portfolio = result.portfolio_history

    assert portfolio.iloc[0]["Shares"] == 1000
    assert portfolio.iloc[0]["Cash"] == 0


# ── Multi-Position Accumulation ──────────────────────────────


def test_multiple_buys_accumulate_with_percentage_sizing():
    """
    With 25% sizing, multiple BUY signals should accumulate into one
    position.

    BUY 1: $100k * 25% = $25k -> 250 shares at $100, cash $75k
    BUY 2: portfolio_value = $75k + 250*$105 = $101,250
            allocation = $101,250 * 25% = $25,312.50
            shares = int($25,312.50 // $105) = 241 shares
            investment = 241 * $105 = $25,305
            cash = $75,000 - $25,305 = $49,695
    SELL:   total shares = 250 + 241 = 491
    """

    df = create_sample_dataframe(
        signals=["BUY", "BUY", "SELL"],
        prices=[100, 105, 120],
    )

    sizing = PositionSizingConfig(
        sizing_type="fixed_percentage",
        sizing_parameters={"percent": 0.25},
    )

    result = simulate_portfolio(
        df,
        position_sizing_config=sizing,
    )

    portfolio = result.portfolio_history

    # After first BUY
    assert portfolio.iloc[0]["Shares"] == 250

    # After second BUY - shares should increase
    assert portfolio.iloc[1]["Shares"] > 250

    # After SELL - all shares sold
    assert portfolio.iloc[2]["Shares"] == 0

    # Should record 1 completed trade with 2 entries
    assert len(result.trade_history) == 1

    trade = result.trade_history.iloc[0]
    assert trade["num_entries"] == 2
    assert trade["first_entry_date"] == pd.Timestamp("2024-01-01")


def test_accumulation_weighted_average_entry_price():
    """
    Verify weighted average entry price with accumulation.

    BUY 1: 100 shares at $100 = $10,000
    BUY 2: 100 shares at $120 = $12,000
    Total: 200 shares, $22,000, avg $110
    SELL at $130: exit_value = $26,000, profit = $4,000
    """

    df = create_sample_dataframe(
        signals=["BUY", "BUY", "SELL"],
        prices=[100, 120, 130],
    )

    sizing = PositionSizingConfig(
        sizing_type="fixed_shares",
        sizing_parameters={"shares": 100},
    )

    result = simulate_portfolio(
        df,
        position_sizing_config=sizing,
    )

    portfolio = result.portfolio_history

    assert portfolio.iloc[0]["Shares"] == 100
    assert portfolio.iloc[1]["Shares"] == 200

    trade = result.trade_history.iloc[0]
    assert trade["entry_price"] == 110  # Weighted average
    assert trade["shares"] == 200
    assert trade["investment"] == 22000
    assert trade["exit_value"] == 26000
    assert trade["profit_loss"] == 4000
    assert trade["num_entries"] == 2


def test_accumulation_with_insufficient_cash_on_second_buy():
    """
    When a second BUY signal comes but cash is insufficient for any
    shares, the position should remain unchanged.
    """

    df = create_sample_dataframe(
        signals=["BUY", "BUY", "SELL"],
        prices=[100, 105, 120],
    )

    # All-in on first buy leaves no cash for second
    result = simulate_portfolio(df)

    portfolio = result.portfolio_history

    assert portfolio.iloc[0]["Shares"] == 1000
    assert portfolio.iloc[0]["Cash"] == 0

    # Second BUY: no cash available, shares unchanged
    assert portfolio.iloc[1]["Shares"] == 1000
    assert portfolio.iloc[1]["Cash"] == 0

    trade = result.trade_history.iloc[0]
    assert trade["num_entries"] == 1


def test_stop_loss_with_accumulated_position():
    """
    Stop-loss should use weighted average entry price with
    accumulated positions.

    BUY 1: 100 shares at $100
    BUY 2: 100 shares at $110
    Avg entry: $105
    5% stop-loss on avg: $105 * 0.95 = $99.75
    Price drops to $99 -> stop triggered
    """

    df = create_sample_dataframe(
        signals=["BUY", "BUY", "HOLD", "HOLD"],
        prices=[100, 110, 105, 99],
    )

    sizing = PositionSizingConfig(
        sizing_type="fixed_shares",
        sizing_parameters={"shares": 100},
    )

    result = simulate_portfolio(
        df,
        risk_config=RiskConfig(
            stop_loss_type="fixed_percentage",
            stop_loss_parameters={"percent": 0.05},
        ),
        position_sizing_config=sizing,
    )

    assert result.summary["completed_trade_count"] == 1

    trade = result.trade_history.iloc[0]
    assert trade["exit_reason"] == "stop_loss"
    assert trade["num_entries"] == 2
    assert trade["shares"] == 200
    assert trade["entry_price"] == 105  # Weighted average


def test_take_profit_with_accumulated_position():
    """
    Take-profit should use weighted average entry price with
    accumulated positions.

    BUY 1: 100 shares at $100
    BUY 2: 100 shares at $110
    Avg entry: $105
    20% take-profit: $105 * 1.20 = $126
    Price rises to $126 -> take-profit triggered
    """

    df = create_sample_dataframe(
        signals=["BUY", "BUY", "HOLD", "HOLD"],
        prices=[100, 110, 120, 126],
    )

    sizing = PositionSizingConfig(
        sizing_type="fixed_shares",
        sizing_parameters={"shares": 100},
    )

    result = simulate_portfolio(
        df,
        risk_config=RiskConfig(
            take_profit_type="fixed_percentage",
            take_profit_parameters={"percent": 0.20},
        ),
        position_sizing_config=sizing,
    )

    assert result.summary["completed_trade_count"] == 1

    trade = result.trade_history.iloc[0]
    assert trade["exit_reason"] == "take_profit"
    assert trade["num_entries"] == 2
    assert trade["shares"] == 200
    assert trade["entry_price"] == 105  # Weighted average


def test_buy_sell_buy_sell_with_sizing():
    """
    Two complete round-trip trades with position sizing.
    Each trade should be independent.
    """

    df = create_sample_dataframe(
        signals=["BUY", "SELL", "BUY", "SELL"],
        prices=[100, 110, 100, 120],
    )

    sizing = PositionSizingConfig(
        sizing_type="fixed_shares",
        sizing_parameters={"shares": 100},
    )

    result = simulate_portfolio(
        df,
        position_sizing_config=sizing,
    )

    assert len(result.trade_history) == 2

    trade1 = result.trade_history.iloc[0]
    assert trade1["shares"] == 100
    assert trade1["entry_price"] == 100
    assert trade1["exit_price"] == 110
    assert trade1["num_entries"] == 1

    trade2 = result.trade_history.iloc[1]
    assert trade2["shares"] == 100
    assert trade2["entry_price"] == 100
    assert trade2["exit_price"] == 120
    assert trade2["num_entries"] == 1


def test_holding_period_uses_first_entry():
    """
    Holding period should be measured from the first entry.
    """

    df = create_sample_dataframe(
        signals=["BUY", "BUY", "HOLD", "SELL"],
        prices=[100, 110, 115, 120],
    )

    sizing = PositionSizingConfig(
        sizing_type="fixed_shares",
        sizing_parameters={"shares": 100},
    )

    result = simulate_portfolio(
        df,
        position_sizing_config=sizing,
    )

    trade = result.trade_history.iloc[0]
    assert trade["holding_period"] == 3  # From index 0 to index 3
