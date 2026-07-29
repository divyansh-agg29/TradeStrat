# Phase 1 — Foundation

## Objective
Prepare the project structure for a reusable risk-management layer before implementing the actual stop-loss logic.

## Goals
- Create a dedicated risk module.
- Add a configuration model for risk settings.
- Extend the backtest request model so risk settings can flow into the simulation pipeline.
- Keep the implementation backward compatible.

## Tasks

### 1. Create the risk package
Add a new package such as:
- risk/__init__.py
- risk/config.py
- risk/rules.py
- risk/manager.py

The package should contain the initial logic for:
- fixed stop-loss configuration
- stop-loss evaluation
- future extensibility for other exit rules

### 2. Add a risk configuration model
Create a dataclass or simple config object to hold the initial settings:
- stop_loss_enabled: bool
- stop_loss_percent: float

This should be optional so existing backtests continue to work without it.

### 3. Extend the backtest request model
Update the request model to accept a new optional field:
- risk: RiskConfig | None

This ensures the risk settings can be passed from the API layer into the backtest service and portfolio simulator.

### 4. Keep defaults safe
If no risk configuration is supplied:
- no stop loss is applied
- the simulator behaves exactly as it does today

This is important for regression safety.

## Design decisions for future-proofing
- Keep the risk config object separate from strategy config.
- Make the risk module responsible only for decision-making, not portfolio bookkeeping.
- Define a simple interface such as:
  - evaluate_trade(open_trade, current_price, current_date) -> decision

That interface will make it easy to add take-profit or trailing-stop rules later.

## Acceptance criteria
- A new risk module exists.
- Backtest requests can carry optional risk configuration.
- Existing backtests without risk settings still run normally.
- The project is ready for the simulator integration step.
