# Phase 1 — Data Models

## Objective

Create the dataclasses that represent a comparison request and its results. These models are the foundation that all subsequent phases depend on.

---

## Scope

### New Files

#### `models/comparison_request.py`

A frozen dataclass representing the input to a comparison run.

```python
from dataclasses import dataclass, field
from models.strategy_config import StrategyConfig


@dataclass(frozen=True)
class ComparisonRequest:
    """
    Represents a strategy comparison request.

    Common parameters are shared across all strategies.
    Each strategy entry specifies its own type and parameters.
    """
    ticker: str
    start_date: str
    end_date: str
    initial_capital: float = 100000.0
    risk_free_rate: float = 0.0
    strategies: list[StrategyConfig] = field(default_factory=list)
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `ticker` | `str` | — | NSE ticker symbol. |
| `start_date` | `str` | — | Backtest start date (`YYYY-MM-DD`). |
| `end_date` | `str` | — | Backtest end date (`YYYY-MM-DD`). |
| `initial_capital` | `float` | `100000.0` | Starting capital shared by all strategies. |
| `risk_free_rate` | `float` | `0.0` | Annual risk-free rate (decimal). |
| `strategies` | `list[StrategyConfig]` | `[]` | 2–6 strategy configurations to compare. |

#### `models/comparison_result.py`

Two dataclasses: one for individual strategy outcomes and one for the aggregated comparison.

```python
from dataclasses import dataclass
from typing import Optional
from models.strategy_config import StrategyConfig
from models.backtest_result import BacktestResult


@dataclass
class StrategyResult:
    """
    Result for a single strategy within a comparison.

    On success, backtest_result contains the full BacktestResult.
    On failure, backtest_result is None and error describes what went wrong.
    """
    strategy: StrategyConfig
    success: bool
    error: Optional[str] = None
    backtest_result: Optional[BacktestResult] = None


@dataclass(frozen=True)
class ComparisonResult:
    """
    Aggregated result for a full comparison run.

    Contains the original request (for echoing common parameters)
    and an ordered list of per-strategy results.
    """
    request: ComparisonRequest
    strategy_results: list[StrategyResult]
```

**`StrategyResult` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `strategy` | `StrategyConfig` | The strategy config this result corresponds to. |
| `success` | `bool` | `True` if the backtest completed without error. |
| `error` | `Optional[str]` | Error message on failure, `None` on success. |
| `backtest_result` | `Optional[BacktestResult]` | Full backtest output on success, `None` on failure. |

**`ComparisonResult` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `request` | `ComparisonRequest` | The original request (used to echo common params in the response). |
| `strategy_results` | `list[StrategyResult]` | Ordered list of per-strategy results. Same order as `request.strategies`. |

### Modified Files

#### `models/__init__.py`

Add exports for all three new classes:

```python
from .comparison_request import ComparisonRequest
from .comparison_result import StrategyResult, ComparisonResult
```

Update `__all__` to include `ComparisonRequest`, `StrategyResult`, `ComparisonResult`.

---

## Verification

After this phase, the following should work:

```python
from models import ComparisonRequest, StrategyResult, ComparisonResult, StrategyConfig

# Create a request
req = ComparisonRequest(
    ticker="RELIANCE.NS",
    start_date="2020-01-01",
    end_date="2024-12-31",
    strategies=[
        StrategyConfig(type="sma_crossover", parameters={"short_period": 20, "long_period": 50}),
        StrategyConfig(type="ema_crossover", parameters={"short_period": 12, "long_period": 26}),
    ],
)

# Create a result (empty for now)
result = ComparisonResult(request=req, strategy_results=[])
```

No unit test file is needed for this phase — the models are simple dataclasses. They will be exercised by the service and serializer tests in Phases 2 and 3.

---

## Dependencies

- None. This is the first phase.

## Depended On By

- Phase 2 (Comparison Service) — uses `ComparisonRequest`, `ComparisonResult`, `StrategyResult`.
- Phase 3 (Comparison Serializer) — uses `ComparisonResult`.
- Phase 4 (API Route) — uses `ComparisonRequest`.
