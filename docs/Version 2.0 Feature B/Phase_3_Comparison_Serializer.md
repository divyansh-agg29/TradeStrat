# Phase 3 — Comparison Serializer

## Objective

Implement the serialization layer that converts a `ComparisonResult` into a JSON-serializable dictionary for the API response. This serializer reuses the existing `serialize_backtest_result` function per strategy but applies post-processing to strip fields not needed in the comparison context.

---

## Scope

### New Files

#### `serialization/comparison_serializer.py`

A single public function:

```python
def serialize_comparison_result(result: ComparisonResult) -> dict
```

**Step-by-step logic:**

```
1. Build the "common" dict from result.request:
   {
     "ticker": result.request.ticker,
     "start_date": result.request.start_date,
     "end_date": result.request.end_date,
     "initial_capital": result.request.initial_capital,
     "risk_free_rate": result.request.risk_free_rate,
   }

2. Extract benchmark from the FIRST successful strategy result:
   - Find the first StrategyResult where success == True.
   - Call serialize_backtest_result(strategy_result.backtest_result).
   - Extract "benchmark_metrics" from the serialized output.
   - Extract Buy & Hold equity data from the serialized output
     (the benchmark portfolio history for the equity chart).
   - Build:
     benchmark = {
       "portfolio_history": <Buy & Hold equity data>,
       "benchmark_metrics": <serialized benchmark metrics>,
     }
   - If NO strategies succeeded, set benchmark = None.

3. Build the "results" array. For each strategy_result in result.strategy_results:
   a. Build strategy echo:
      {
        "type": strategy_result.strategy.type,
        "parameters": strategy_result.strategy.parameters,
      }
   b. If strategy_result.success:
      - Call serialize_backtest_result(strategy_result.backtest_result)
      - Remove the "kpi_cards" key from the serialized dict.
      - Remove the "benchmark_metrics" key from the serialized dict.
      - Add "strategy", "success": True, "error": None to the dict.
   c. If not strategy_result.success:
      - Emit:
        {
          "strategy": <echo>,
          "success": False,
          "error": strategy_result.error,
          "portfolio_metrics": None,
          "risk_metrics": None,
          "trade_metrics": None,
          "portfolio_history": None,
          "analytics_history": None,
          "trade_history": None,
        }

4. Return:
   {
     "common": <common dict>,
     "benchmark": <benchmark or None>,
     "results": <results array>,
   }
```

**Why strip `kpi_cards`?**

The Compare tab displays metrics in a tabular matrix format sourced directly from `portfolio_metrics`, `risk_metrics`, and `trade_metrics`. KPI cards are a single-backtest UI concept — displaying 10 individual cards per strategy for 2–6 strategies is not practical. The serializer calls `serialize_backtest_result` (which internally builds KPI cards) but removes the `kpi_cards` key before returning.

**Why strip `benchmark_metrics` per strategy?**

All strategies use the same ticker, date range, and initial capital, so the Buy & Hold benchmark is identical across all of them. Including it in every strategy result would be redundant. Instead, it is extracted once and placed in the top-level `benchmark` object.

**Imports needed:**

```python
from models import ComparisonResult
from serialization.backtest_serializer import serialize_backtest_result
```

### Modified Files

#### `serialization/__init__.py`

Add export:

```python
from .comparison_serializer import serialize_comparison_result
```

Update `__all__` to include `"serialize_comparison_result"`.

---

## Unit Tests

### `tests/test_comparison_serializer.py`

Tests use mock `ComparisonResult` objects with mock `BacktestResult` instances (or mock `serialize_backtest_result` to return canned dicts).

| Test | Setup | Assertion |
|------|-------|-----------|
| `test_common_params_echoed` | Any valid result. | `output["common"]` has correct `ticker`, `start_date`, `end_date`, `initial_capital`, `risk_free_rate`. |
| `test_successful_strategy_serialized` | One successful strategy. | Result entry has `success=True`, `error=None`, and non-null `portfolio_metrics`, `risk_metrics`, `trade_metrics`, `portfolio_history`, `analytics_history`, `trade_history`. |
| `test_kpi_cards_stripped` | One successful strategy. | `"kpi_cards" not in output["results"][0]`. |
| `test_benchmark_metrics_stripped_from_results` | One successful strategy. | `"benchmark_metrics" not in output["results"][0]`. |
| `test_benchmark_extracted_to_top_level` | Two strategies, first succeeds. | `output["benchmark"]` is not None. Contains `"portfolio_history"` and `"benchmark_metrics"` keys. |
| `test_benchmark_null_when_all_fail` | Two strategies, both fail. | `output["benchmark"] is None`. |
| `test_failed_strategy_serialized` | One failed strategy. | Entry has `success=False`, `error` is a string, all metric/history fields are `None`. |
| `test_strategy_config_echoed` | Two strategies with different types. | Each `output["results"][i]["strategy"]` has correct `type` and `parameters`. |
| `test_results_order_matches_request` | Three strategies. | `output["results"][0]["strategy"]["type"]` matches first strategy, etc. |

---

## Output Shape Reference

Successful strategy entry:
```json
{
  "strategy": { "type": "sma_crossover", "parameters": { ... } },
  "success": true,
  "error": null,
  "portfolio_metrics": { ... },
  "risk_metrics": { ... },
  "trade_metrics": { ... },
  "portfolio_history": [ ... ],
  "analytics_history": [ ... ],
  "trade_history": [ ... ]
}
```

Failed strategy entry:
```json
{
  "strategy": { "type": "ema_crossover", "parameters": { ... } },
  "success": false,
  "error": "No trades generated for this strategy.",
  "portfolio_metrics": null,
  "risk_metrics": null,
  "trade_metrics": null,
  "portfolio_history": null,
  "analytics_history": null,
  "trade_history": null
}
```

Keys that are **NOT** present in comparison results: `kpi_cards`, `benchmark_metrics`.

---

## Verification

After this phase:

1. `pytest tests/test_comparison_serializer.py` passes all tests.
2. The full existing test suite still passes.

---

## Dependencies

- Phase 1 (Models) — `ComparisonResult`, `StrategyResult`.
- Existing `serialization/backtest_serializer.py` — `serialize_backtest_result` is called internally.

## Depended On By

- Phase 4 (API Route) — calls `serialize_comparison_result`.
