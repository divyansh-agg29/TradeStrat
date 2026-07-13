from pathlib import Path

from data.service import get_stock_data
from indicators import calculate_sma, calculate_ema, calculate_rsi, calculate_macd
from strategy import generate_sma_crossover_signals, generate_ema_crossover_signals, generate_macd_crossover_signals
from portfolio import simulate_portfolio
from analytics import analyze_performance


# ============================================================================
# Output Directory
# ============================================================================

OUTPUT_DIR = Path("manual_verification_output")
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================================
# Download Market Data
# ============================================================================

df = get_stock_data(
    ticker="RELIANCE.NS",
    start_date="2025-01-01",
    end_date="2026-07-01",
)



# ============================================================================
# Generate Trading Signals
# ============================================================================

df = generate_macd_crossover_signals(df)

df.to_csv(
    OUTPUT_DIR / "strategy_result.csv"
)


# # ============================================================================
# # Run Portfolio Simulation
# # ============================================================================

# simulation_result = simulate_portfolio(df)

# simulation_result.portfolio_history.to_csv(
#     OUTPUT_DIR / "portfolio_history.csv"
# )

# simulation_result.trade_history.to_csv(
#     OUTPUT_DIR / "trade_history.csv",
#     index=False,
# )


# # ============================================================================
# # Print Simulation Summary
# # ============================================================================

# print("\nSimulation Summary")
# print("=" * 60)

# for key, value in simulation_result.summary.items():
#     print(f"{key}: {value}")


# # ============================================================================
# # Run Performance Analytics
# # ============================================================================

# analytics_result = analyze_performance(
#     simulation_result
# )

# analytics_result.analytics_history.to_csv(
#     OUTPUT_DIR / "analytics_history.csv"
# )


# # ============================================================================
# # Print Portfolio Metrics
# # ============================================================================

# print("\nPortfolio Metrics")
# print("=" * 60)
# print(analytics_result.portfolio_metrics)


# # ============================================================================
# # Print Risk Metrics
# # ============================================================================

# print("\nRisk Metrics")
# print("=" * 60)
# print(analytics_result.risk_metrics)


# # ============================================================================
# # Print Trade Metrics
# # ============================================================================

# print("\nTrade Metrics")
# print("=" * 60)
# print(analytics_result.trade_metrics)


# # ============================================================================
# # Preview Analytics History
# # ============================================================================

# print("\nAnalytics History (First 10 Rows)")
# print("=" * 60)
# print(analytics_result.analytics_history.head(10))

# print("\nAnalytics History (Last 10 Rows)")
# print("=" * 60)
# print(analytics_result.analytics_history.tail(10))


# print("\nManual verification completed successfully.")
# print(f"All output files have been saved to: {OUTPUT_DIR.resolve()}")