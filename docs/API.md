# TradeStrat REST API Documentation

## Overview

The TradeStrat REST API provides endpoints for executing historical trading strategy backtests, comparing multiple trading strategies, and monitoring application health.

All requests and responses use the `application/json` content type.

---

# Base URL

## Local Development

```text
http://localhost:5000
```

## Production

```text
https://tradestrat.onrender.com/
```

---

# Authentication

The current version of TradeStrat does not require authentication.

All endpoints are publicly accessible. To prevent accidental abuse, rate limiting is applied to computationally expensive endpoints.

---

# Common Error Response

Unless otherwise stated, failed requests return a JSON response in the following format.

```json
{
    "success": false,
    "error": {
        "type": "ErrorType",
        "message": "error message"
    }
}
```

Example:

```json
{
    "success": false,
    "error": {
        "type": "ValueError",
        "message": "Invalid Ticker"
    }
}
```

---

# Pages

## Landing Page

```http
GET /
```

Serves the landing page HTML.

## Dashboard

```http
GET /app
```

Serves the main application dashboard HTML.

---

# Health Check

Returns the current health status of the application.

## Endpoint

```http
GET /health
```

## Example Response

```json
{
    "success": true,
    "data": {
        "status": "healthy"
    }
}
```

## Status Codes

| Code | Description            |
| ---- | ---------------------- |
| 200  | Application is healthy |

---

# Run Backtest

Executes a historical backtest for a single trading strategy.

## Endpoint

```http
POST /backtest
```

Rate limit: 5 requests per minute.

---

## Request Body

```json
{
    "ticker": "RELIANCE.NS",
    "start_date": "2024-01-01",
    "end_date": "2025-01-01",
    "initial_capital": 100000,
    "risk_free_rate": 0.06,
    "interval": "1d",
    "strategy": {
        "type": "sma_crossover",
        "parameters": {
            "short_period": 20,
            "long_period": 50
        }
    },
    "risk": {
        "stop_loss_type": "fixed_percentage",
        "parameters": {
            "percent": 0.05
        },
        "take_profit_type": "fixed_amount",
        "take_profit_parameters": {
            "amount": 300
        }
    },
    "position_sizing": {
        "sizing_type": "kelly_criterion",
        "parameters": {
            "win_rate": 0.55,
            "win_loss_ratio": 1.5,
            "kelly_fraction": 0.5
        }
    }
}
```

---

## Request Fields

| Field                                | Type   | Required | Default  | Description                                  |
| ------------------------------------ | ------ | -------- | -------- | -------------------------------------------- |
| ticker                               | string | Yes      |          | Stock ticker symbol                          |
| start_date                           | string | Yes      |          | Start date (`YYYY-MM-DD`)                    |
| end_date                             | string | Yes      |          | End date (`YYYY-MM-DD`)                      |
| initial_capital                      | number | No       | 100000   | Initial portfolio capital                    |
| risk_free_rate                       | number | No       | 0.0      | Annual risk-free rate as a decimal (e.g. 0.06 = 6%) |
| interval                             | string | No       | `"1d"`   | Data interval for the backtest               |
| strategy.type                        | string | Yes      |          | Strategy identifier                          |
| strategy.parameters                  | object | Yes      |          | Strategy-specific configuration              |
| risk.stop_loss_type                  | string | No       |          | Stop-loss identifier                         |
| risk.parameters                      | object | No       |          | Stop-loss specific configuration             |
| risk.take_profit_type                | string | No       |          | Take-profit identifier                       |
| risk.take_profit_parameters          | object | No       |          | Take-profit specific configuration           |
| position_sizing.sizing_type          | string | No       |          | Position sizing identifier                   |
| position_sizing.parameters           | object | No       |          | Position sizing specific configuration       |

---

## Available Strategies

| Type                 | Parameters                            |
| -------------------- | ------------------------------------- |
| `sma_crossover`      | `short_period`, `long_period`         |
| `ema_crossover`      | `short_period`, `long_period`         |
| `macd_crossover`     | `fast_period`, `slow_period`, `signal_period` |
| `rsi_mean_reversion` | `period`, `overbought`, `oversold`    |
| `bb_bounce`          | `period`, `std_multiplier`            |

## Available Intervals

| Interval | Description |
| -------- | ----------- |
| `1m`     | 1 Minute    |
| `5m`     | 5 Minutes   |
| `15m`    | 15 Minutes  |
| `30m`    | 30 Minutes  |
| `1h`     | 1 Hour      |
| `1d`     | 1 Day       |
| `1wk`    | 1 Week      |
| `1mo`    | 1 Month     |

## Available Stop-Loss Types

| Type                  | Parameters  |
| --------------------- | ----------- |
| `fixed_percentage`    | `percent`   |
| `fixed_price_offset`  | `offset`    |
| `trailing_stop`       | `percent`   |

## Available Take-Profit Types

| Type                  | Parameters  |
| --------------------- | ----------- |
| `fixed_percentage`    | `percent`   |
| `fixed_amount`        | `amount`    |

## Available Position Sizing Types

| Type                | Parameters                                      |
| ------------------- | ----------------------------------------------- |
| `all_in`            | _(none)_                                        |
| `fixed_percentage`  | `percent`                                       |
| `fixed_amount`      | `amount`                                        |
| `fixed_shares`      | `shares`                                        |
| `risk_based`        | `risk_percent`                                  |
| `kelly_criterion`   | `win_rate`, `win_loss_ratio`, `kelly_fraction`  |

---

## Success Response

A successful request returns a JSON object containing the complete backtest results.

Response structure:

```json
{
    "success": true,
    "data": {
        "analytics_history": [ ... ],
        "benchmark_metrics": { ... },
        "charts": { ... },
        "kpi_cards": { ... },
        "portfolio_history": [ ... ],
        "portfolio_metrics": { ... },
        "risk_metrics": { ... },
        "trade_history": [ ... ],
        "trade_metrics": { ... }
    }
}
```

### Response Objects

| Object            | Description                                |
| ----------------- | ------------------------------------------ |
| analytics_history | List of analytics data                     |
| benchmark_metrics | Buy & Hold comparison metrics              |
| charts            | Data required to render frontend charts    |
| kpi_cards         | Summary metrics displayed in the dashboard |
| portfolio_history | List of daily portfolio data               |
| portfolio_metrics | Portfolio performance statistics           |
| risk_metrics      | Risk-adjusted performance metrics          |
| trade_history     | List of completed trades                   |
| trade_metrics     | Trade statistics                           |

---

## Status Codes

| Code | Description                     |
| ---- | ------------------------------- |
| 200  | Backtest completed successfully |
| 400  | Invalid request                 |
| 429  | Rate limit exceeded             |
| 500  | Internal server error           |

---

# Compare Strategies

Executes multiple strategy backtests using identical market conditions and returns a consolidated comparison.

## Endpoint

```http
POST /compare
```

Rate limit: 5 requests per minute.

---

## Request Body

```json
{
    "ticker": "RELIANCE.NS",
    "start_date": "2024-01-01",
    "end_date": "2025-01-01",
    "initial_capital": 100000,
    "risk_free_rate": 0.06,
    "interval": "1d",
    "strategies": [
        {
            "type": "sma_crossover",
            "parameters": {
                "short_period": 20,
                "long_period": 50
            }
        },
        {
            "type": "ema_crossover",
            "parameters": {
                "short_period": 20,
                "long_period": 50
            }
        }
    ]
}
```

---

## Request Fields

| Field                  | Type   | Required | Default  | Description                                  |
| ---------------------- | ------ | -------- | -------- | -------------------------------------------- |
| ticker                 | string | Yes      |          | Stock ticker symbol                          |
| start_date             | string | Yes      |          | Start date (`YYYY-MM-DD`)                    |
| end_date               | string | Yes      |          | End date (`YYYY-MM-DD`)                      |
| initial_capital        | number | No       | 100000   | Initial portfolio capital                    |
| risk_free_rate         | number | No       | 0.0      | Annual risk-free rate as a decimal (e.g. 0.06 = 6%) |
| interval               | string | No       | `"1d"`   | Data interval for the backtest               |
| strategies             | array  | Yes      |          | List of 2-6 strategy configurations          |
| strategies[].type      | string | Yes      |          | Strategy identifier                          |
| strategies[].parameters| object | Yes      |          | Strategy-specific configuration              |

---

## Success Response

```json
{
    "success": true,
    "data": {
        "common": {
            "ticker": "RELIANCE.NS",
            "start_date": "2024-01-01",
            "end_date": "2025-01-01",
            "initial_capital": 100000,
            "risk_free_rate": 0.06,
            "interval": "1d"
        },
        "benchmark": {
            "portfolio_history": [ ... ],
            "benchmark_metrics": { ... }
        },
        "results": [
            {
                "strategy": { "type": "sma_crossover", "parameters": { ... } },
                "success": true,
                "error": null,
                "portfolio_metrics": { ... },
                "risk_metrics": { ... },
                "trade_metrics": { ... },
                "portfolio_history": [ ... ],
                "analytics_history": [ ... ],
                "trade_history": [ ... ],
                "charts": { ... }
            }
        ]
    }
}
```

### Response Objects

| Object              | Description                                                        |
| -------------------- | ------------------------------------------------------------------ |
| common               | Shared request parameters echoed back                              |
| benchmark            | Buy & Hold benchmark data from the first successful strategy       |
| results              | Array of per-strategy results                                      |
| results[].strategy   | Strategy type and parameters echoed back                           |
| results[].success    | Whether the strategy executed successfully                         |
| results[].error      | Error message if the strategy failed, otherwise `null`             |

Each successful element in `results` contains the same response objects as the `/backtest` endpoint (excluding `kpi_cards` and `benchmark_metrics`).

---

## Status Codes

| Code | Description                       |
| ---- | --------------------------------- |
| 200  | Comparison completed successfully |
| 400  | Invalid request                   |
| 429  | Rate limit exceeded               |
| 500  | Internal server error             |

---

# HTTP Status Codes

| Status Code | Meaning                               |
| ----------- | ------------------------------------- |
| 200         | Request completed successfully        |
| 400         | Invalid request or validation failure |
| 404         | Endpoint not found                    |
| 405         | HTTP method not supported             |
| 429         | Rate limit exceeded                   |
| 500         | Unexpected server error               |

---
