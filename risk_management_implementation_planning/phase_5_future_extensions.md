# Phase 5 — Future Extensions

## Objective
Design the initial implementation so future risk-management features can be added without rewriting the system.

## Future features to support later

### 1. Take-profit exits
Add support for:
- fixed target price
- fixed target percentage
- risk-reward-based targets

### 2. Trailing stop losses
Implement rules where:
- the stop moves upward as price rises
- the stop is locked in once the trade becomes profitable

### 3. Break-even stops
Allow the stop to move to entry price once the trade reaches a specified profit threshold.

### 4. ATR-based risk rules
Use volatility-based stop losses so stops adapt to market conditions.

### 5. Position sizing
Extend the risk layer to support:
- fixed fractional sizing
- risk-per-trade sizing
- volatility-adjusted sizing

### 6. Portfolio-level constraints
Add controls such as:
- max open positions
- max daily loss
- max drawdown limit

## Design choices that will help later
- Keep the risk engine separate from strategies and analytics.
- Use a pluggable rule interface so new rules can be added easily.
- Store enough metadata in each completed trade to power richer reporting later.
- Keep the risk configuration object open for new fields even if they are unused initially.

## Final vision
Once the foundation is in place, the app can evolve from a simple strategy backtester into a more realistic risk-aware trading research platform.
