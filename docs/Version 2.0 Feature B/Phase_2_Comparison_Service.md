# Phase 2 — Comparison Service

## Objective

Implement the orchestration logic that accepts a `ComparisonRequest`, runs each strategy sequentially via the existing `run_backtest` function, and returns a `ComparisonResult`.

---

## Scope

### New Files

#### `services/comparison_service.py`

A single public function:

```python
def run_comparison(request: ComparisonRequest) -> ComparisonResult
```

**Sequential execution logic:**

```
1. Validate ComparisonRequest:
   - len(request.strategies) must be between 2 and 6 (inclusive).
   - If not, raise ValueError("A comparison requires between 2 and 6 strategies.").
   - Common params (ticker, dates, capital) are NOT validated here —
     they are validated inside run_backtest for each strategy.

2. Initialize an empty list: strategy_results = []

3. For each strategy_config in request.strategies:
   a. Build a BacktestRequest from the shared params + this strategy:
        BacktestRequest(
            ticker=request.ticker,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            risk_free_rate=request.risk_free_rate,
            strategy=strategy_config,
        )
   b. try:
        result = run_backtest(backtest_request)
        strategy_results.append(
            StrategyResult(strategy=strategy_config, success=True, backtest_result=result)
        )
      except Exception as exc:
        strategy_results.append(
            StrategyResult(strategy=strategy_config, success=False, error=str(exc))
        )

4. Return ComparisonResult(request=request, strategy_results=strategy_results)
```

**Key behaviors:**

- **No short-circuiting** — If strategy #2 fails, strategies #3–#6 still execute.
- **Error isolation** — Each strategy runs in its own try/except. One failure does not affect others.
- **Market data caching** — The first strategy triggers a Yahoo Finance download. Subsequent strategies for the same ticker/date range hit the Market Data Store cache automatically. No special logic needed here; the caching is transparent via `get_stock_data` inside `run_backtest`.

**Imports needed:**

```python
import logging
from models import (
    BacktestRequest, StrategyConfig,
    ComparisonRequest, ComparisonResult, StrategyResult,
)
from services.backtest_service import run_backtest
```

### Modified Files

#### `services/__init__.py`

Add export:

```python
from .comparison_service import run_comparison
```

Update `__all__` to include `"run_comparison"`.

---

## Unit Tests

### `tests/test_comparison_service.py`

All tests mock `run_backtest` to avoid real market data downloads.

| Test | Setup | Assertion |
|------|-------|-----------|
| `test_valid_comparison_two_strategies` | Mock `run_backtest` to return a dummy `BacktestResult` for both calls. | `len(result.strategy_results) == 2`, both have `success=True`. |
| `test_valid_comparison_six_strategies` | Mock `run_backtest` to succeed 6 times. | `len(result.strategy_results) == 6`, all `success=True`. |
| `test_failed_strategy_included_with_error` | Mock `run_backtest` to succeed on first call and raise `Exception("No trades")` on second. | First result `success=True`, second `success=False` with `error="No trades"`. |
| `test_all_strategies_fail` | Mock `run_backtest` to always raise. | All results have `success=False`, each with an `error` string. |
| `test_fewer_than_two_strategies_raises` | Pass 1 strategy. | `pytest.raises(ValueError)`. |
| `test_more_than_six_strategies_raises` | Pass 7 strategies. | `pytest.raises(ValueError)`. |
| `test_empty_strategies_raises` | Pass 0 strategies. | `pytest.raises(ValueError)`. |
| `test_market_data_shared` | Mock `run_backtest` for 3 strategies. Inside the mock, track calls to `get_stock_data`. | `get_stock_data` called 3 times (once per `run_backtest`), but the Market Data Store ensures only 1 actual download. At the mock level, verify `run_backtest` is called 3 times with correct `BacktestRequest` objects. |
| `test_result_order_matches_request` | Pass 3 different strategies. | `result.strategy_results[i].strategy == request.strategies[i]` for each `i`. |
| `test_request_echoed_in_result` | Pass any valid request. | `result.request is request` (same object reference). |

**Test helper:**

Create a helper function to build a minimal `ComparisonRequest`:

```python
def make_comparison_request(num_strategies=2):
    strategies = [
        StrategyConfig(type="sma_crossover", parameters={"short_period": 20, "long_period": 50})
        for _ in range(num_strategies)
    ]
    return ComparisonRequest(
        ticker="TEST.NS",
        start_date="2020-01-01",
        end_date="2024-12-31",
        strategies=strategies,
    )
```

---

## Verification

After this phase:

1. `pytest tests/test_comparison_service.py` passes all tests.
2. The full existing test suite still passes (`pytest` from project root).

---

## Dependencies

- Phase 1 (Models) — `ComparisonRequest`, `ComparisonResult`, `StrategyResult` must exist.
- Existing `services/backtest_service.py` — `run_backtest` is called internally.
- Existing `models/backtest_request.py` — `BacktestRequest` is constructed per strategy.

## Depended On By

- Phase 4 (API Route) — calls `run_comparison`.
