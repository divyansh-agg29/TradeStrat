from dataclasses import dataclass


@dataclass(frozen=True)
class AllInPositionSizing:
    """
    All-in position sizing rule.

    Uses all available cash to buy the maximum number of whole shares.
    This is the default behavior (current system behavior).
    """

    def calculate_shares(
        self,
        portfolio_value: float,
        cash: float,
        current_price: float,
        stop_loss_price: float | None = None,
    ) -> int:
        """
        Return the number of shares to buy using all available cash.
        """

        if current_price <= 0 or cash <= 0:
            return 0

        return int(cash // current_price)


@dataclass(frozen=True)
class FixedPercentagePositionSizing:
    """
    Fixed percentage position sizing rule.

    Allocates a fixed percentage of the current portfolio value
    to each trade.

    Parameters
    ----------
    percent : float
        Fraction of portfolio value to allocate (0 < percent <= 1).
        E.g. 0.25 means 25% of portfolio value per trade.
    """

    percent: float

    def __post_init__(self) -> None:
        if self.percent <= 0:
            raise ValueError("percent must be greater than zero")
        if self.percent > 1:
            raise ValueError("percent must not exceed 1.0")

    def calculate_shares(
        self,
        portfolio_value: float,
        cash: float,
        current_price: float,
        stop_loss_price: float | None = None,
    ) -> int:
        """
        Return the number of shares to buy based on a fixed percentage
        of current portfolio value, limited by available cash.
        """

        if current_price <= 0 or cash <= 0 or portfolio_value <= 0:
            return 0

        allocation = portfolio_value * self.percent
        affordable = min(allocation, cash)

        return int(affordable // current_price)


@dataclass(frozen=True)
class FixedAmountPositionSizing:
    """
    Fixed dollar amount position sizing rule.

    Allocates a fixed dollar amount to each trade.

    Parameters
    ----------
    amount : float
        Dollar amount to allocate per trade.
    """

    amount: float

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError("amount must be greater than zero")

    def calculate_shares(
        self,
        portfolio_value: float,
        cash: float,
        current_price: float,
        stop_loss_price: float | None = None,
    ) -> int:
        """
        Return the number of shares to buy based on a fixed dollar
        amount, limited by available cash.
        """

        if current_price <= 0 or cash <= 0:
            return 0

        affordable = min(self.amount, cash)

        return int(affordable // current_price)


@dataclass(frozen=True)
class FixedSharesPositionSizing:
    """
    Fixed shares position sizing rule.

    Always buys a fixed number of shares, limited by available cash.

    Parameters
    ----------
    shares : int
        Number of shares to buy per trade.
    """

    shares: int

    def __post_init__(self) -> None:
        if self.shares <= 0:
            raise ValueError("shares must be greater than zero")

    def calculate_shares(
        self,
        portfolio_value: float,
        cash: float,
        current_price: float,
        stop_loss_price: float | None = None,
    ) -> int:
        """
        Return the fixed number of shares, or fewer if cash is
        insufficient.
        """

        if current_price <= 0 or cash <= 0:
            return 0

        max_affordable = int(cash // current_price)

        return min(self.shares, max_affordable)


@dataclass(frozen=True)
class RiskBasedPositionSizing:
    """
    Risk-based position sizing rule.

    Sizes the position based on a maximum risk tolerance per trade.
    The number of shares is calculated so that the dollar risk
    (entry price - stop loss price) per share times the number of
    shares equals the desired risk amount.

    Formula: shares = (portfolio_value * risk_percent) / (current_price - stop_loss_price)

    Parameters
    ----------
    risk_percent : float
        Fraction of portfolio value to risk per trade (0 < risk_percent <= 1).
        E.g. 0.02 means risk 2% of portfolio per trade.
    """

    risk_percent: float

    def __post_init__(self) -> None:
        if self.risk_percent <= 0:
            raise ValueError("risk_percent must be greater than zero")
        if self.risk_percent > 1:
            raise ValueError("risk_percent must not exceed 1.0")

    def calculate_shares(
        self,
        portfolio_value: float,
        cash: float,
        current_price: float,
        stop_loss_price: float | None = None,
    ) -> int:
        """
        Return the number of shares to buy based on risk tolerance.

        If no stop-loss price is provided, falls back to all-in
        behavior (uses all available cash).
        """

        if current_price <= 0 or cash <= 0 or portfolio_value <= 0:
            return 0

        if stop_loss_price is None or stop_loss_price >= current_price:
            return int(cash // current_price)

        risk_per_share = current_price - stop_loss_price
        risk_budget = portfolio_value * self.risk_percent
        shares = int(risk_budget // risk_per_share)

        max_affordable = int(cash // current_price)

        return min(shares, max_affordable)


POSITION_SIZING_REGISTRY: dict[str, type] = {
    "all_in": AllInPositionSizing,
    "fixed_percentage": FixedPercentagePositionSizing,
    "fixed_amount": FixedAmountPositionSizing,
    "fixed_shares": FixedSharesPositionSizing,
    "risk_based": RiskBasedPositionSizing,
}
