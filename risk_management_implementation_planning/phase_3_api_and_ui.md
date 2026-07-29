# Phase 3 — API and UI Integration

## Objective
Expose the fixed stop-loss feature through the application interface so a user can configure it and run a backtest with it enabled.

## Goals
- Accept stop-loss settings in the API request payload.
- Pass the risk settings through the service layer into the simulator.
- Add a simple frontend control for configuring a stop-loss percentage.
- Keep the UI minimal and future-friendly.

## Backend tasks

### 1. Extend the API request parsing
Update the request parsing flow in the API layer so that a stop-loss value can be received from the incoming JSON payload.

Expected payload example:

```json
{
  "ticker": "RELIANCE.NS",
  "start_date": "2020-01-01",
  "end_date": "2024-01-01",
  "initial_capital": 100000,
  "strategy": {
    "type": "sma_crossover",
    "parameters": {}
  },
  "risk": {
    "stop_loss_percent": 0.03
  }
}
```

### 2. Pass risk settings to the backtest service
The backtest service should accept and forward the risk configuration to the portfolio simulator.

### 3. Preserve backward compatibility
If the payload does not include a risk block, the system should behave exactly as before.

## Frontend tasks

### 1. Add a new risk section to the control panel
Add a simple input, for example:
- Stop Loss %

This field should be optional and default to blank or disabled when not used.

### 2. Send the value to the backend
When the user runs a backtest, include the configured stop-loss percentage in the request payload.

### 3. Keep the UI structure extensible
The UI should be designed so additional risk controls can be added later, such as:
- take profit
- trailing stop
- risk per trade

A dedicated risk section makes this easy.

## Acceptance criteria
- The API accepts stop-loss configuration.
- The backend applies the configured stop-loss rule during a backtest.
- The frontend allows a user to set a stop-loss percentage.
- The feature works even when the input is left empty.
