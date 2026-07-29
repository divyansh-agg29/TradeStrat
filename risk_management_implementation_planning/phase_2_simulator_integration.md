# Phase 2 — Simulator Integration

## Objective
Implement the actual stop-loss behavior inside the portfolio simulator so that open positions are closed automatically when they hit the configured threshold.

## Goals
- Apply a fixed stop-loss rule during backtest execution.
- Close trades based on the daily close price.
- Record the exit with enough detail to support future analytics.
- Preserve the current signal-based behavior when no stop loss is configured.

## Detailed implementation plan

### 1. Update the portfolio simulation loop
The current simulator loops over each row in the market data and processes the signal. In this phase, the loop should also evaluate whether an open trade should be stopped.

For each row:
1. Read the current close price.
2. Check whether there is an open trade.
3. If a risk rule exists, evaluate whether the stop-loss threshold is hit.
4. If yes, close the trade immediately.
5. Otherwise, continue with the normal signal processing.

### 2. Define the stop-loss decision logic
For a long position:
- if current_close <= entry_price * (1 - stop_loss_percent), trigger stop loss

For a short position:
- if current_close >= entry_price * (1 + stop_loss_percent), trigger stop loss

Because the current project only supports long trades from the existing simulator, the first implementation can focus on long-only exits.

### 3. Close the trade with a stop-loss exit reason
When the stop is triggered, the trade should:
- update cash and holdings
- mark the position as flat
- create a completed trade record
- record an exit reason such as stop_loss

This should be distinct from a standard signal-driven exit.

### 4. Preserve trade history structure
The completed trade object should be enriched to include:
- exit_reason
- stop_loss_price
- exit_type

This keeps the schema future-ready for take-profit and trailing-stop exits.

### 5. Ensure the order of operations is correct
The simulator should decide the stop-loss exit before or alongside the strategy signal, depending on the design. A practical approach is:
- evaluate stop loss first
- then process the signal for that bar

This ensures that a stop-loss exit is not missed just because a SELL signal also appears later in the same day.

## Edge cases to handle
- No open trade exists
- Stop-loss not configured
- Entry price is zero or invalid
- Stop-loss percentage is negative or missing
- A trade hits the stop-loss on the same day it is entered

## Acceptance criteria
- A trade closes automatically when the stop-loss threshold is reached.
- The trade history includes enough data to identify that the exit was caused by a stop loss.
- The existing simulator behavior remains unchanged when risk settings are absent.
