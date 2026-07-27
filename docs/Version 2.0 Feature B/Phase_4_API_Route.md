# Phase 4 — API Route

## Objective

Add the `POST /compare` endpoint to `api/routes.py`. This endpoint parses the incoming JSON, builds a `ComparisonRequest`, calls the comparison service, serializes the result, and returns it as JSON. Error handling mirrors the existing `/backtest` endpoint.

---

## Scope

### Modified Files

#### `api/routes.py`

**New route:**

```python
@api.route("/compare", methods=["POST"])
def compare():
    """
    Execute a strategy comparison.
    Accepts 2–6 strategy configurations with shared common parameters.
    """
    try:
        data = request.get_json(force=True)
        comparison_request = _parse_comparison_request(data)
        comparison_result = run_comparison(comparison_request)
        serialized = serialize_comparison_result(comparison_result)

        return jsonify({"success": True, "data": serialized})

    except (ValueError, KeyError) as exc:
        return jsonify({
            "success": False,
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
            }
        }), 400

    except Exception as exc:
        return jsonify({
            "success": False,
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
            }
        }), 500
```

**New helper function:**

```python
def _parse_comparison_request(data: dict) -> ComparisonRequest:
    """
    Parse raw JSON dict into a ComparisonRequest.

    Extracts common parameters (ticker, dates, capital, risk_free_rate)
    and builds a list of StrategyConfig objects from the strategies array.
    """
    strategies_raw = data.get("strategies", [])

    strategies = [
        StrategyConfig(
            type=s.get("type", ""),
            parameters=s.get("parameters", {}),
        )
        for s in strategies_raw
    ]

    return ComparisonRequest(
        ticker=data.get("ticker", ""),
        start_date=data.get("start_date", ""),
        end_date=data.get("end_date", ""),
        initial_capital=float(data.get("initial_capital", 100000)),
        risk_free_rate=float(data.get("risk_free_rate", 0.0)),
        strategies=strategies,
    )
```

**New imports at the top of `routes.py`:**

```python
from models import ComparisonRequest, StrategyConfig
from services import run_comparison
from serialization import serialize_comparison_result
```

Note: `StrategyConfig` may already be imported. Only add what's missing.

---

## Request/Response Contract

### Request

```
POST /compare
Content-Type: application/json
```

```json
{
  "ticker": "RELIANCE.NS",
  "start_date": "2020-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 100000,
  "risk_free_rate": 0.0,
  "strategies": [
    { "type": "sma_crossover", "parameters": { "short_period": 20, "long_period": 50 } },
    { "type": "ema_crossover", "parameters": { "short_period": 12, "long_period": 26 } }
  ]
}
```

### Success Response (HTTP 200)

```json
{
  "success": true,
  "data": {
    "common": { ... },
    "benchmark": { ... },
    "results": [ ... ]
  }
}
```

### Validation Error (HTTP 400)

Triggered by: fewer than 2 strategies, more than 6, missing fields, bad ticker, bad dates.

```json
{
  "success": false,
  "error": {
    "type": "ValueError",
    "message": "A comparison requires between 2 and 6 strategies."
  }
}
```

### Server Error (HTTP 500)

Triggered by: unexpected exceptions not caught by service-level error isolation.

```json
{
  "success": false,
  "error": {
    "type": "RuntimeError",
    "message": "..."
  }
}
```

---

## Error Flow

| Error Source | HTTP Status | Handling |
|-------------|-------------|----------|
| Invalid JSON body | 400 | Caught by `request.get_json` or `_parse_comparison_request`. |
| Missing required fields | 400 | `ValueError` or `KeyError` from parsing. |
| Strategy count out of range | 400 | `ValueError` raised by `run_comparison` validation. |
| Individual strategy failure | 200 | Handled inside `run_comparison` — failed strategy appears in results with `success=False`. |
| All strategies fail individually | 200 | Response still `success=True` at top level. All entries have `success=False`. |
| Unexpected exception | 500 | Generic catch-all. |

---

## Integration Tests

These tests use Flask's test client. Mock `run_backtest` to avoid real downloads.

| Test | Setup | Assertion |
|------|-------|-----------|
| `test_compare_endpoint_success` | Valid payload with 2 strategies, mock `run_backtest` to succeed. | HTTP 200, `response["success"] == True`, `len(response["data"]["results"]) == 2`. |
| `test_compare_endpoint_invalid_json` | Send malformed body. | HTTP 400. |
| `test_compare_endpoint_too_few_strategies` | Payload with 1 strategy. | HTTP 400, error message mentions strategy count. |
| `test_compare_endpoint_too_many_strategies` | Payload with 7 strategies. | HTTP 400. |
| `test_compare_endpoint_missing_ticker` | Payload with empty ticker. | HTTP 400 or 500 (depending on where validation fires). |
| `test_compare_endpoint_partial_failure` | 3 strategies, one raises. | HTTP 200, 2 results with `success=True`, 1 with `success=False`. |

Test file location: These can be added to `tests/test_comparison_service.py` as a separate test class, or placed in a new `tests/test_compare_route.py`. Decide based on preference.

---

## Verification

After this phase, the full backend is complete:

1. All new tests pass.
2. The full existing test suite still passes.
3. Manual test with `curl` or Postman:

```bash
curl -X POST http://localhost:5000/compare \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "RELIANCE.NS",
    "start_date": "2020-01-01",
    "end_date": "2024-12-31",
    "initial_capital": 100000,
    "strategies": [
      {"type": "sma_crossover", "parameters": {"short_period": 20, "long_period": 50}},
      {"type": "ema_crossover", "parameters": {"short_period": 12, "long_period": 26}}
    ]
  }'
```

Expected: HTTP 200 with `success: true` and two entries in `data.results`.

---

## Dependencies

- Phase 1 (Models) — `ComparisonRequest`, `StrategyConfig`.
- Phase 2 (Comparison Service) — `run_comparison`.
- Phase 3 (Comparison Serializer) — `serialize_comparison_result`.

## Depended On By

- Phases 5–8 (Frontend) — the frontend calls this endpoint.
