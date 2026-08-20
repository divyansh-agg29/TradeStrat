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


@dataclass(frozen=True)
class KellyCriterionPositionSizing:
    """
    Kelly Criterion position sizing rule.

    Calculates optimal position size based on historical win rate
    and win/loss ratio to maximize long-term capital growth.

    Formula: Kelly % = W - [(1 - W) / R]

    Where:
        W = Win rate (probability of a winning trade)
        R = Win/Loss ratio (average win / average loss)

    A fractional Kelly multiplier is applied to reduce volatility.

    Parameters
    ----------
    win_rate : float
        Historical win rate as a fraction (0 < win_rate < 1).
        E.g. 0.55 means 55 % of trades are winners.

    win_loss_ratio : float
        Average winning trade divided by average losing trade
        (must be > 0).  E.g. 1.5 means the average win is 1.5x
        the average loss.

    kelly_fraction : float
        Fraction of the full Kelly percentage to use
        (0 < kelly_fraction <= 1).  Defaults to 0.5 (half-Kelly).
    """

    win_rate: float
    win_loss_ratio: float
    kelly_fraction: float = 0.5

    def __post_init__(self) -> None:
        if self.win_rate <= 0 or self.win_rate >= 1:
            raise ValueError(
                "win_rate must be between 0 and 1 (exclusive)"
            )
        if self.win_loss_ratio <= 0:
            raise ValueError(
                "win_loss_ratio must be greater than zero"
            )
        if self.kelly_fraction <= 0 or self.kelly_fraction > 1:
            raise ValueError(
                "kelly_fraction must be between 0 (exclusive) and 1 (inclusive)"
            )

    def calculate_shares(
        self,
        portfolio_value: float,
        cash: float,
        current_price: float,
        stop_loss_price: float | None = None,
    ) -> int:
        """
        Return the number of shares to buy using the Kelly Criterion.

        The raw Kelly percentage is clamped to [0, 1] so that a
        negative edge produces zero shares rather than a short.
        """

        if current_price <= 0 or cash <= 0 or portfolio_value <= 0:
            return 0

        kelly_percent = (
            self.win_rate
            - (1 - self.win_rate) / self.win_loss_ratio
        )

        adjusted_kelly = kelly_percent * self.kelly_fraction
        adjusted_kelly = max(0.0, min(adjusted_kelly, 1.0))

        allocation = portfolio_value * adjusted_kelly
        affordable = min(allocation, cash)

        return int(affordable // current_price)


POSITION_SIZING_REGISTRY: dict[str, type] = {
    "all_in": AllInPositionSizing,
    "fixed_percentage": FixedPercentagePositionSizing,
    "fixed_amount": FixedAmountPositionSizing,
    "fixed_shares": FixedSharesPositionSizing,
    "risk_based": RiskBasedPositionSizing,
    "kelly_criterion": KellyCriterionPositionSizing,
}
