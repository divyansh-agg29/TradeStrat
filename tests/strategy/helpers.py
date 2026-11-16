import pandas as pd


def create_market_data(close_prices):
    """Create a standard market DataFrame for testing."""

    return pd.DataFrame(
        {
            "Open": close_prices,
            "High": close_prices,
            "Low": close_prices,
            "Close": close_prices,
            "Volume": [1000] * len(close_prices),
        }
    )
