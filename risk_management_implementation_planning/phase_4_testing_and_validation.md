# Phase 4 — Testing and Validation

## Objective
Verify that the fixed stop-loss feature works correctly and that the existing backtest flow remains stable.

## Test areas

### 1. Unit tests for risk configuration
Test that:
- risk settings are parsed correctly
- stop-loss percentage values are accepted and stored
- invalid values are rejected gracefully

### 2. Unit tests for stop-loss evaluation
Test that:
- a stop-loss is triggered when the price falls past the threshold
- a stop-loss is not triggered when the price remains above the threshold
- the logic works for a simple long position example

### 3. Simulator integration tests
Test that:
- a trade is closed via stop loss when the threshold is reached
- the portfolio cash and holdings are updated correctly
- the trade history includes the stop-loss exit reason

### 4. Regression tests
Ensure the following still work:
- backtests without risk settings continue to work
- standard signal-based exits still occur normally
- analytics output remains correct

## Validation checklist
- The feature works on a small known dataset.
- The stop-loss exit is reflected in the trade history.
- The resulting portfolio curve changes in a reasonable way.
- No existing strategy or analytics test regresses.

## Acceptance criteria
- All new tests pass.
- Existing tests still pass.
- The feature behaves correctly in both default and configured modes.
