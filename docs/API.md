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
    "success": True/False,
    "error": {
        "type": ErrorType,
        "message": "error message",
    },
}
```

Example:

```json
{
    "success": False,
    "error": {
        "type": ValueError,
        "message": "Invalid Ticker",
    },
}
```

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
    "success": True,
    "data": {
        "status": "healthy",
    },
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

---

## Request Body

```json
{
    "ticker": "RELIANCE.NS",
    "start_date": "2024-01-01",
    "end_date": "2025-01-01",
    "initial_capital": 100000,
    "strategy": {
        "type": "sma_crossover",
        "parameters": {
            "short_period": 20,
            "long_period": 50
        }
    },
    "risk": {
        "stop_loss_type" : "fixed_percentage",
        "parameters":{
            "percent": 0.05
        },
        "take_profit_type": "fixed_amount",
        "take_profit_parameters": {
            "amount": 300
        }
    }
}
```

---

## Request Fields

| Field                       | Type   | Description                          |
| ----------------------------| ------ | ------------------------------------ |
| ticker                      | string | Stock ticker symbol                  |
| start_date                  | string | Start date (`YYYY-MM-DD`)            |
| end_date                    | string | End date (`YYYY-MM-DD`)              |
| initial_capital             | number | Initial portfolio capital            |
| strategy.type               | string | Strategy identifier                  |
| strategy.parameters         | object | Strategy-specific configuration      |
| risk.stop_loss_type         | string | Stop Loss identifier                 |             
| risk.parameters             | object | Stop loss specific configuration     |
| risk.take_profit_type       | string | Take profit identifier               |
| risk.take_profit_parameters | object | Take profit specific configuration   |
---

## Success Response

A successful request returns a JSON object containing the complete backtest results.

Response structure:

```json
{
    "analytics_history": [ ... ],
    "benchmark_metrics": { ... },
    "charts": { ... },
    "kpi_cards": { ... },
    "portfolio_history": [ ... ],
    "portfolio_metrics": { ... },
    "risk_metrics": { ... },
    "trade_history":[ ... ],
    "trade_metrics": { ... }
}
```

### Response Objects

| Object            | Description                                |
| ----------------- | ------------------------------------------ |
| analytics_history | List of Analytics data                     |
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

> **Note:** Available from Version 2.0 onward.

## Endpoint

```http
POST /compare
```

---

## Request Body

```json
{
    "ticker": "RELIANCE.NS",
    "start_date": "2024-01-01",
    "end_date": "2025-01-01",
    "initial_capital": 100000,
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

## Success Response

```json
{
    "results": [
        { ... },
        { ... }
    ]
}
```

Each element in the `results` array follows the same response schema as the `/backtest` endpoint.

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
