# Fixed Stop-Loss Risk Modelling Plan

## Goal
Add a first version of risk modelling with a fixed stop-loss rule that works end-to-end in the current backtest pipeline, while leaving room for future additions such as take-profit, trailing stops, and dynamic position sizing.

## Why this feature matters
The current backtest flow only closes trades when the strategy emits a SELL signal. A stop-loss system makes the simulation more realistic and gives users a way to control downside risk explicitly.

## Scope of the first version
Support one simple risk rule:
- fixed percentage stop loss from entry price

The system should:
- accept stop-loss settings from the request payload
- evaluate open trades during portfolio simulation
- close trades when the stop-loss threshold is met
- record the stop-loss exit in trade history
- remain backward compatible when no risk settings are provided

## High-level architecture
The implementation should introduce a dedicated risk layer that sits between strategy signals and portfolio execution.

Suggested flow:
1. Strategy generates a signal.
2. Risk manager evaluates the current open trade.
3. If a stop-loss threshold is hit, the trade closes.
4. Otherwise the existing signal-based execution continues.
5. Portfolio state and analytics are updated as usual.

## Implementation phases
1. Foundation
   - add a risk configuration model
   - extend the backtest request model
   - create a new risk module with a fixed stop-loss rule

2. Simulator integration
   - modify portfolio simulation to evaluate open trades each day
   - enforce stop loss when the closing price breaches the threshold
   - record exit reason and exit details

3. API and UI integration
   - expose stop-loss settings through the API
   - add a simple frontend field for stop-loss percentage

4. Testing and validation
   - add unit tests for stop-loss behavior
   - verify backward compatibility and default behavior

5. Future-ready design
   - structure the module so that take-profit, trailing stops, and sizing can be added later

## Design principles
- Keep risk logic separate from the strategy engine.
- Keep the portfolio simulator responsible for trade execution and state updates.
- Make new risk controls optional and backward compatible.
- Design the module around pluggable rules so future features can be added without major refactoring.

## Expected outcomes
After implementation, users should be able to:
- configure a stop-loss percentage
- run a backtest with that stop loss applied
- see trades closed earlier due to risk management
- compare strategy performance with and without risk controls
