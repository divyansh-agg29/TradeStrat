# Strategy Comparison Tab — Detailed Design

## Overview

The Strategy Comparison Tab allows users to run 2–6 trading strategies on the same ticker, date range, and initial capital, then view their performance side-by-side. All strategies receive identical market data, ensuring a fair comparison. Results are displayed in a dedicated "Compare" tab alongside the existing single-backtest view, with a metrics comparison matrix, overlaid equity curves, overlaid drawdown charts, and per-strategy trade history.

A "strategy" in the context of comparison is defined by its **type + parameters combination**. Two entries with the same type but different parameters (e.g., SMA Crossover with 20/50 and SMA Crossover with 10/30) are treated as distinct strategies.

This feature builds on top of the existing backtest infrastructure. The single-backtest workflow remains completely unchanged. A new `POST /compare` endpoint accepts a list of strategy configurations and executes them sequentially, reusing the existing `run_backtest` function internally. Market data is downloaded once and cached via the Market Data Store (Version 2A), so subsequent strategies in the same comparison run hit the cache and avoid redundant Yahoo Finance calls.

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Execution model | Sequential | Simplest to implement and debug. Market data caching eliminates the main latency source (repeated downloads). |
| API surface | New `POST /compare` endpoint | Clean separation from existing `/backtest`. Different request/response shape. |
| Orchestration module | New `services/comparison_service.py` | Keeps `backtest_service.py` unchanged. Single responsibility. |
| Data models | New `ComparisonRequest` + `ComparisonResult` dataclasses | Explicit shared-parameter model. Clear distinction from single-backtest types. |
| Serialization | New `serialization/comparison_serializer.py` | Reuses `serialize_backtest_result` per strategy, strips KPI cards and benchmark metrics, adds comparison structure. |
| Failed strategy handling | Include with error marker | One bad strategy does not block the rest. User sees which ones failed and why. |
| Frontend placement | Separate tab in existing page | Users can switch between single-backtest and comparison without navigating away. |
| Winner / Primary objective | Not implemented | Deferred to a future release. The tab shows raw side-by-side analytics only. |

---

## API Contract

### Endpoint

```
POST /compare
Content-Type: application/json
```

### Request Body

```json
{
  "ticker": "RELIANCE.NS",
  "start_date": "2020-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 100000,
  "risk_free_rate": 0.0,
  "strategies": [
    {
      "type": "sma_crossover",
      "parameters": { "short_period": 20, "long_period": 50 }
    },
    {
      "type": "ema_crossover",
      "parameters": { "short_period": 12, "long_period": 26 }
    },
    {
      "type": "rsi_mean_reversion",
      "parameters": { "rsi_period": 14, "oversold": 30, "overbought": 70 }
    }
  ]
}
```

**Fields:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `ticker` | string | yes | — | NSE ticker symbol (e.g. `"RELIANCE.NS"`). |
| `start_date` | string | yes | — | Backtest start date (`YYYY-MM-DD`). |
| `end_date` | string | yes | — | Backtest end date (`YYYY-MM-DD`). |
| `initial_capital` | number | no | `100000` | Starting capital for each strategy. |
| `risk_free_rate` | number | no | `0.0` | Annual risk-free rate for Sharpe/Sortino. |
| `strategies` | array | yes | — | 2–6 strategy configuration objects. |

Each element in `strategies` has:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | yes | Strategy identifier from `STRATEGY_REGISTRY` (`sma_crossover`, `ema_crossover`, `macd_crossover`, `rsi_mean_reversion`). |
| `parameters` | object | no | Strategy-specific parameters. Defaults to empty `{}` (strategy uses its own defaults). |

**Validation rules:**

- `strategies` must contain **2–6** entries. Fewer than 2 or more than 6 returns a 400 error.
- Common parameters (`ticker`, `start_date`, `end_date`) are validated identically to the existing `/backtest` endpoint.
- Each strategy's `type` is validated against `STRATEGY_REGISTRY`. An unrecognized type causes that individual strategy to fail (not the entire request).

### Response Body (Success — HTTP 200)

```json
{
  "success": true,
  "data": {
    "common": {
      "ticker": "RELIANCE.NS",
      "start_date": "2020-01-01",
      "end_date": "2024-12-31",
      "initial_capital": 100000,
      "risk_free_rate": 0.0
    },
    "benchmark": {
      "portfolio_history": [ ... ],
      "benchmark_metrics": { ... }
    },
    "results": [
      {
        "strategy": {
          "type": "sma_crossover",
          "parameters": { "short_period": 20, "long_period": 50 }
        },
        "success": true,
        "error": null,
        "portfolio_metrics": { ... },
        "risk_metrics": { ... },
        "trade_metrics": { ... },
        "portfolio_history": [ ... ],
        "analytics_history": [ ... ],
        "trade_history": [ ... ]
      },
      {
        "strategy": {
          "type": "ema_crossover",
          "parameters": { "short_period": 12, "long_period": 26 }
        },
        "success": false,
        "error": "No trades generated for this strategy.",
        "portfolio_metrics": null,
        "risk_metrics": null,
        "trade_metrics": null,
        "portfolio_history": null,
        "analytics_history": null,
        "trade_history": null
      }
    ]
  }
}
```

**Response structure:**

- `common` — Echoes back the shared parameters for display in the results header.
- `benchmark` — Benchmark data extracted once from the first successful strategy's result (see Benchmark Handling below).
- `results` — Ordered array (same order as the request's `strategies`), one entry per strategy.

**Top-level `benchmark` object:**

Because all strategies use the same ticker, date range, and initial capital, the Buy & Hold benchmark is identical across all of them. Rather than repeating it in every strategy result, it is extracted once and placed at the top level.

| Field | Type | Description |
|-------|------|-------------|
| `portfolio_history` | array | Buy & Hold equity curve data points (date + value). Used to render a single dotted benchmark trace on the equity chart. |
| `benchmark_metrics` | object | Benchmark final value, benchmark return, alpha. Provided for reference but not displayed in the Compare tab UI. |

If all strategies fail, `benchmark` is `null`.

**Per-strategy result entry:**

| Field | Type | Description |
|-------|------|-------------|
| `strategy` | object | Echoed strategy config (`type` + `parameters`). |
| `success` | boolean | Whether this strategy's backtest completed without error. |
| `error` | string or null | Error message if the backtest failed, otherwise `null`. |
| `portfolio_metrics` | object or null | Same structure as existing `/backtest` response. `null` on failure. |
| `risk_metrics` | object or null | Same structure as existing `/backtest` response. `null` on failure. |
| `trade_metrics` | object or null | Same structure as existing `/backtest` response. `null` on failure. |
| `portfolio_history` | array or null | Same structure as existing `/backtest` response. `null` on failure. |
| `analytics_history` | array or null | Same structure as existing `/backtest` response. `null` on failure. |
| `trade_history` | array or null | Same structure as existing `/backtest` response. `null` on failure. |

**Intentionally excluded per-strategy fields:**

- `kpi_cards` — Not included. The Compare tab displays metrics in a tabular matrix format, not individual KPI cards. Generating KPI card objects for 2–6 strategies would be wasteful. The comparison serializer calls `serialize_backtest_result` internally but **strips the `kpi_cards` key** from each result before including it in the response.
- `benchmark_metrics` — Not included per-strategy. Benchmark data is identical across all strategies and is provided once at the top level instead.

The existing `serialize_backtest_result` function is reused internally for each successful strategy, with post-processing to remove the excluded fields.

### Response Body (Validation Error — HTTP 400)

```json
{
  "success": false,
  "error": {
    "type": "ValueError",
    "message": "A comparison requires between 2 and 6 strategies."
  }
}
```

Validation errors that affect the entire request (bad ticker, bad dates, strategy count out of range) return 400 with no partial results. Per-strategy failures (bad strategy type, no trades generated) are captured inside the `results` array instead.

---

## New Data Models

### `models/comparison_request.py`

```python
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

### `models/comparison_result.py`

```python
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

### `models/__init__.py` changes

Add exports for `ComparisonRequest`, `ComparisonResult`, and `StrategyResult`.

---

## Backend Modules

### `services/comparison_service.py`

This module contains a single public function:

```python
def run_comparison(request: ComparisonRequest) -> ComparisonResult
```

**Sequential execution logic:**

```
1. Validate ComparisonRequest:
   - strategies list must have 2–6 entries.
   - (Ticker/date/capital validation happens inside run_backtest.)

2. For each strategy in request.strategies:
   a. Build a BacktestRequest:
        BacktestRequest(
            ticker=request.ticker,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            risk_free_rate=request.risk_free_rate,
            strategy=strategy_config,
        )
   b. Try: call run_backtest(backtest_request)
      - On success → StrategyResult(strategy=..., success=True, backtest_result=result)
      - On exception → StrategyResult(strategy=..., success=False, error=str(exc))

3. Return ComparisonResult(request=request, strategy_results=[...])
```

**Key behaviors:**

- **No short-circuiting**: If strategy #2 fails, strategies #3–#6 still execute.
- **Market data caching**: The first strategy triggers a download. Strategies #2–#6 hit the Market Data Store cache because they use the same ticker and date range. The warm-up period extension (1 year prior) produces the same extended range for all strategies, so the cache key matches exactly.
- **Error isolation**: Each strategy runs in its own try/except. Errors from one strategy do not affect others.

### `serialization/comparison_serializer.py`

This module contains a single public function:

```python
def serialize_comparison_result(result: ComparisonResult) -> dict
```

**Logic:**

```
1. Build "common" dict from result.request:
   {
     "ticker": ...,
     "start_date": ...,
     "end_date": ...,
     "initial_capital": ...,
     "risk_free_rate": ...,
   }

2. Extract benchmark from the first successful strategy result:
   - Serialize its benchmark_metrics.
   - Extract Buy & Hold equity curve from its portfolio_history or analytics.
   - If no strategies succeeded, set benchmark to null.

3. For each strategy_result in result.strategy_results:
   a. Build strategy echo:
      { "type": ..., "parameters": ... }
   b. If strategy_result.success:
      - Call serialize_backtest_result(strategy_result.backtest_result)
      - Remove "kpi_cards" key from the serialized output.
      - Remove "benchmark_metrics" key from the serialized output.
      - Merge with { "strategy": ..., "success": True, "error": None }
   c. If not strategy_result.success:
      - Emit { "strategy": ..., "success": False, "error": strategy_result.error,
               all metric/history fields set to None }

4. Return { "common": ..., "benchmark": ..., "results": [...] }
```

The existing `serialize_backtest_result` function is reused internally. The comparison serializer performs two post-processing steps on each successful result:
- **Strips `kpi_cards`** — KPI cards are a single-backtest UI concept. The Compare tab uses a metrics matrix built directly from `portfolio_metrics`, `risk_metrics`, and `trade_metrics`.
- **Strips `benchmark_metrics`** — Benchmark is identical across strategies and is provided once at the top level.

### `api/routes.py` — new route

A new `POST /compare` route is added to the existing `routes.py`:

```python
@api.route("/compare", methods=["POST"])
def compare():
    """
    Execute a strategy comparison.
    """
    # 1. Parse JSON body.
    # 2. Build ComparisonRequest (extract common params + strategies array).
    # 3. Call run_comparison(comparison_request).
    # 4. Call serialize_comparison_result(comparison_result).
    # 5. Return JSON response.
    # Error handling mirrors existing /backtest route structure.
```

A new `_parse_comparison_request(data)` helper extracts the request fields and builds `ComparisonRequest` with a list of `StrategyConfig` objects.

### Module exports

| File | Addition |
|------|----------|
| `services/__init__.py` | Export `run_comparison` |
| `serialization/__init__.py` | Export `serialize_comparison_result` |
| `models/__init__.py` | Export `ComparisonRequest`, `ComparisonResult`, `StrategyResult` |

---

## Frontend Changes

### Tab System

Two tab buttons are added to the page, sitting between the header and the main content area:

```
[ Backtest ]  [ Compare ]
```

- **Backtest** tab (default, active on page load) — Shows the existing control panel and dashboard exactly as they are today. No changes to existing behavior.
- **Compare** tab — Shows a modified control panel (comparison configuration form) and a comparison results area.

Tab switching is handled by toggling CSS `display` on the two content sections. No page reload or route change.

### Control Panel — Compare Mode

When the Compare tab is active, the control panel renders:

**Shared parameters** (reused from existing form):
- Ticker input
- Start Date input
- End Date input
- Initial Capital input

**Strategy list area** (new):
- A vertically scrollable region containing 2–6 strategy entry blocks.
- Each entry block contains:
  - A strategy type dropdown (same options as existing: SMA Crossover, EMA Crossover, MACD Crossover, RSI Mean Reversion).
  - Dynamic parameter inputs that update when the strategy type changes (reusing the existing `STRATEGY_REGISTRY` parameter definitions from `strategies.js`).
  - A "Remove" button (disabled when only 2 entries remain).
- An "Add Strategy" button below the list (disabled when 6 entries are present).
- A "Run Comparison" button at the bottom.

**Validation:**
- Minimum 2 strategies enforced. The "Remove" button is disabled on the last two entries.
- Maximum 6 strategies enforced. The "Add Strategy" button is disabled at 6.
- Per-strategy parameter validation reuses the existing `validate()` functions from `STRATEGY_REGISTRY`.
- All validation errors shown inline before the request is sent.

### Compare Results Area

When a comparison completes, the Compare tab's results area renders four sections:

#### 1. Summary Header

A compact header showing the common parameters:
- Ticker, date range, initial capital
- Number of strategies compared
- Number of successful / failed strategies

#### 2. Metrics Comparison Matrix

An HTML table comparing key metrics across strategies. This replaces the individual KPI cards used in the single-backtest view — displaying 10 KPI cards per strategy for 2–6 strategies would not be practical, so the Compare tab uses a compact tabular format instead.

**Structure:**

|  | SMA Crossover (20/50) | SMA Crossover (10/30) | RSI MR (14, 30/70) |
|--|---|---|---|
| CAGR | 12.5% | 15.2% | 8.1% |
| Sharpe Ratio | 1.2 | **1.8** | 0.9 |
| Sortino Ratio | 1.5 | **2.1** | 1.0 |
| Max Drawdown | 18.5% | **12.3%** | 22.7% |
| Total Return | 85.2% | 102.4% | 45.8% |
| Win Rate | 55.0% | 58.3% | 48.2% |
| Profit Factor | 1.4 | **1.9** | 1.1 |
| Total Trades | 24 | 31 | 42 |

Note: The example above shows two entries of the same strategy type (SMA Crossover) with different parameters — this is a valid and expected use case.

**Column headers**: Strategy type with a short parameter summary (e.g., "SMA (20/50)"). When the same strategy type appears multiple times with different parameters, the parameter summary differentiates them.

**Row metrics**: Values are sourced directly from `portfolio_metrics`, `risk_metrics`, and `trade_metrics` in each strategy result. No KPI cards are involved.

**Row highlighting**: The best value in each row receives a subtle green background. For Max Drawdown, the lowest absolute value is best. For all other metrics, the highest value is best. Failed strategies show "Error" in all cells and are excluded from best-value highlighting.

**Metric values**: Formatted using the existing `formatByType` function from `formatters.js` (`percentage`, `currency`, `number`, `integer`).

#### 3. Equity Curve Overlay Chart

A single Plotly chart with one trace per successful strategy plus one benchmark trace:
- X-axis: Date
- Y-axis: Portfolio Value
- Each strategy assigned a distinct color from the strategy palette (6 colors)
- **One Buy & Hold benchmark trace** rendered as a **dotted grey line**, sourced from the top-level `benchmark.portfolio_history` in the response. This is the same benchmark regardless of how many strategies are compared.
- Legend identifies each strategy and the benchmark
- Interactive zoom/pan (Plotly default)
- Failed strategies are omitted from the chart

Data source: `portfolio_history` from each strategy result (same data used for the existing single-strategy equity chart). Benchmark data from the top-level `benchmark` object.

#### 4. Drawdown Comparison Chart

A single Plotly chart with one trace per successful strategy:
- X-axis: Date
- Y-axis: Drawdown percentage (negative axis)
- Same color mapping as the equity chart
- Legend identifies each strategy
- Failed strategies omitted

Data source: `analytics_history` from each strategy result (same data used for the existing single-strategy drawdown chart).

#### 5. Per-Strategy Trade History (Expandable)

A tabbed section where each tab corresponds to one strategy. Clicking a tab shows the trade history table for that strategy. The table structure is identical to the existing trade history table. Failed strategies show an error message instead of a table.

### Loading State

When a comparison is running, the existing loading overlay is reused with updated text: "Running Comparison... (Strategy 2 of 4)" — though the sequential execution happens server-side in one request, so the overlay simply shows "Running Comparison..." without live progress updates. Live per-strategy progress can be added in a future version.

### Color Palette

Six distinct colors for the strategy traces:

| Index | Color | Hex |
|-------|-------|-----|
| 1 | Blue | `#2196F3` |
| 2 | Orange | `#FF9800` |
| 3 | Green | `#4CAF50` |
| 4 | Red | `#F44336` |
| 5 | Purple | `#9C27B0` |
| 6 | Teal | `#009688` |

### New Frontend Files

| File | Purpose |
|------|---------|
| `frontend/static/js/compare.js` | Comparison tab logic: form management (add/remove strategy entries, dynamic params), API call to `/compare`, result rendering (matrix, charts, trade history tabs) |
| `frontend/static/css/compare.css` | Styles for tab buttons, strategy list form, comparison matrix table, per-strategy trade tabs |

### Modified Frontend Files

| File | Change |
|------|--------|
| `frontend/templates/index.html` | Add tab button bar, wrap existing dashboard in a backtest-tab container, add compare-tab container with results sections, include new JS/CSS files |
| `frontend/static/js/app.js` | Add tab initialization and switching logic in `initializeApplication` |

---

## File Changes Summary

### New Files

| File | Description |
|------|-------------|
| `models/comparison_request.py` | `ComparisonRequest` dataclass |
| `models/comparison_result.py` | `StrategyResult` + `ComparisonResult` dataclasses |
| `services/comparison_service.py` | `run_comparison` orchestration function |
| `serialization/comparison_serializer.py` | `serialize_comparison_result` function |
| `frontend/static/js/compare.js` | Frontend comparison logic |
| `frontend/static/css/compare.css` | Comparison-specific styles |
| `tests/test_comparison_service.py` | Service unit tests |
| `tests/test_comparison_serializer.py` | Serializer unit tests |

### Modified Files

| File | Change |
|------|--------|
| `models/__init__.py` | Export `ComparisonRequest`, `ComparisonResult`, `StrategyResult` |
| `services/__init__.py` | Export `run_comparison` |
| `serialization/__init__.py` | Export `serialize_comparison_result` |
| `api/routes.py` | Add `POST /compare` route + `_parse_comparison_request` helper |
| `frontend/templates/index.html` | Tab bar, compare-tab container, new script/CSS includes |
| `frontend/static/js/app.js` | Tab switching initialization |

### Unchanged Files

All existing modules remain untouched:
- `data/` — No changes (Market Data Store already handles caching)
- `strategy/` — No changes (strategies are called via existing `run_backtest`)
- `analytics/` — No changes
- `portfolio/` — No changes
- `interpretation/` — No changes (KPI cards still built inside `serialize_backtest_result` but stripped by comparison serializer)
- `services/backtest_service.py` — No changes (reused internally by comparison service)
- `serialization/backtest_serializer.py` — No changes (reused internally by comparison serializer; KPI cards and benchmark metrics stripped post-serialization)
- All existing frontend JS/CSS files — No changes

---

## Execution Flow

### End-to-End Walkthrough

```
User clicks "Run Comparison"
        │
        ▼
Frontend validates inputs (2–6 strategies, params valid)
        │
        ▼
Frontend sends POST /compare { ticker, dates, capital, strategies[] }
        │
        ▼
api/routes.py → _parse_comparison_request() → ComparisonRequest
        │
        ▼
services/comparison_service.py → run_comparison()
        │
        ├─── Strategy 1: run_backtest(BacktestRequest) ── success ── StrategyResult(success=True)
        │         └── get_stock_data() ── cache miss ── download + store
        │
        ├─── Strategy 2: run_backtest(BacktestRequest) ── success ── StrategyResult(success=True)
        │         └── get_stock_data() ── cache hit ── retrieve from DB
        │
        ├─── Strategy 3: run_backtest(BacktestRequest) ── FAILS ─── StrategyResult(success=False)
        │         └── get_stock_data() ── cache hit ── retrieve from DB
        │
        └─── ComparisonResult(strategy_results=[...])
                    │
                    ▼
        serialization/comparison_serializer.py → serialize_comparison_result()
                    │
                    ▼
        api/routes.py → jsonify({ success: true, data: { common, results[] } })
                    │
                    ▼
        Frontend renders: summary header, metrics matrix, equity overlay (+ benchmark dotted line), drawdown overlay, trade tabs
```

### Data Flow for Market Data Caching

All strategies in a comparison use the same ticker and date range. The backtest service adds a 1-year warm-up period before the start date. Since this warm-up calculation is deterministic, all strategies produce the same extended date range for market data retrieval.

- **Strategy 1**: `get_stock_data("RELIANCE.NS", "2019-01-01", "2024-12-31")` → cache miss → downloads from Yahoo Finance → stores in Market Data Store.
- **Strategies 2–6**: `get_stock_data("RELIANCE.NS", "2019-01-01", "2024-12-31")` → cache hit → retrieves from local SQLite database. No API call.

This means a comparison of 6 strategies incurs only **one** Yahoo Finance download, regardless of the number of strategies.

---

## Edge Cases and Error Handling

### Per-Strategy Failures

A strategy can fail for several reasons:
- Invalid strategy type (not in `STRATEGY_REGISTRY`).
- Strategy-specific parameter errors (e.g., short period ≥ long period).
- No trades generated during the backtest period.
- Unexpected runtime errors.

In all cases, the comparison continues with the remaining strategies. The failed strategy appears in the results array with `success: false`, an `error` message, and all metric/history fields set to `null`.

The frontend:
- Shows "Error" in the KPI matrix cells for that strategy's column.
- Omits the strategy's trace from the equity and drawdown charts.
- Shows the error message instead of a trade history table in the per-strategy tab.

### All Strategies Fail

If every strategy in the comparison fails individually, the response is still HTTP 200 with `success: true` at the top level. The `results` array contains all entries with `success: false`. The frontend displays the matrix with all "Error" cells and empty charts.

### Request-Level Validation Failures

These return HTTP 400 before any backtests are attempted:
- Missing `strategies` field.
- Fewer than 2 strategies.
- More than 6 strategies.
- Missing or invalid `ticker`, `start_date`, `end_date`.
- Invalid JSON body.

### Same Strategy Type with Different Parameters

A key use case for the comparison tab is running the same strategy type with different parameter configurations (e.g., SMA Crossover 20/50 vs. SMA Crossover 10/30). Each type + parameters combination is treated as a distinct strategy entry. The column headers in the metrics matrix use the parameter summary to differentiate them.

### Duplicate Strategies (Identical Type + Parameters)

A user can also submit the exact same strategy type with identical parameters multiple times. This is allowed — it may seem redundant but is not harmful. Each entry runs independently and produces identical results.

### Performance Considerations

- **Execution time**: With caching, the primary bottleneck is the first download (~2-5s) plus per-strategy computation (~1-2s each). A 6-strategy comparison should complete in ~10-15s.
- **Memory**: Each `BacktestResult` contains portfolio history, analytics history, and trade history DataFrames. With 6 strategies, all are held in memory simultaneously during serialization. For typical backtests (1000–2500 trading days), this is well within acceptable limits.
- **Response size**: A 6-strategy response with full histories may reach 2–5 MB of JSON. This is acceptable for a single HTTP response but could be optimized with pagination or history truncation in a future version.

---

## Testing Strategy

### `tests/test_comparison_service.py`

| Test | Description |
|------|-------------|
| `test_valid_comparison_two_strategies` | Two valid strategies produce two successful results. |
| `test_valid_comparison_six_strategies` | Six valid strategies produce six successful results. |
| `test_failed_strategy_included_with_error` | One strategy fails, others succeed. Failed entry has `success=False` and `error` string. |
| `test_fewer_than_two_strategies_raises` | Single strategy raises `ValueError`. |
| `test_more_than_six_strategies_raises` | Seven strategies raises `ValueError`. |
| `test_empty_strategies_raises` | Empty list raises `ValueError`. |
| `test_all_strategies_fail` | All strategies fail. Result contains all entries with `success=False`. |
| `test_market_data_shared` | Verify that `get_stock_data` is called only once across multiple strategies (mock level). |

### `tests/test_comparison_serializer.py`

| Test | Description |
|------|-------------|
| `test_common_params_echoed` | `common` dict contains correct ticker, dates, capital, risk_free_rate. |
| `test_successful_strategy_serialized` | Successful entry contains portfolio/risk/trade metrics and histories (non-null). |
| `test_kpi_cards_stripped` | Successful entry does **not** contain `kpi_cards` key. |
| `test_benchmark_metrics_stripped_from_results` | Successful entry does **not** contain `benchmark_metrics` key. |
| `test_benchmark_extracted_to_top_level` | Top-level `benchmark` object contains `portfolio_history` and `benchmark_metrics` from first successful strategy. |
| `test_benchmark_null_when_all_fail` | Top-level `benchmark` is `null` when every strategy fails. |
| `test_failed_strategy_serialized` | Failed entry has `success=False`, `error` string, all metric/history fields `null`. |
| `test_strategy_config_echoed` | Each result entry echoes back its strategy type and parameters. |
| `test_results_order_matches_request` | Results array order matches strategies array order. |

### Route-Level / Integration Tests

| Test | Description |
|------|-------------|
| `test_compare_endpoint_success` | `POST /compare` with valid payload returns 200. |
| `test_compare_endpoint_invalid_json` | Invalid JSON returns 400. |
| `test_compare_endpoint_too_few_strategies` | 1 strategy returns 400. |
| `test_compare_endpoint_too_many_strategies` | 7 strategies returns 400. |

---

## Implementation Order

1. **Models** — `ComparisonRequest`, `StrategyResult`, `ComparisonResult` + `__init__.py` exports.
2. **Comparison Service** — `run_comparison` function + unit tests.
3. **Comparison Serializer** — `serialize_comparison_result` function + unit tests.
4. **API Route** — `POST /compare` endpoint + request parser + integration tests.
5. **Frontend — Tab System** — Tab buttons, switching logic, container structure.
6. **Frontend — Compare Form** — Strategy list form with add/remove, dynamic params.
7. **Frontend — Results Rendering** — KPI matrix, equity overlay, drawdown overlay, trade tabs.
8. **Frontend — Styling** — `compare.css` for matrix, tabs, form layout.

Steps 1–4 (backend) can be completed and tested independently before starting steps 5–8 (frontend).
