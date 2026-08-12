
## Development Changelog

### 2026-08-12 — Multi-Timeframe Support & Intraday Trading
- Added support for 8 trading intervals: 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo
- Implemented interval-specific data availability limits and validation (frontend and backend)
- Added automatic rangebreaks to remove visual gaps from non-trading hours and weekends on intraday charts
- Fixed intraday data storage to preserve hourly timestamps in SQLite cache
- Updated UI to display interval constraints (max range, data availability)

### 2026-08-11 — Data download retry logic
- Added exponential backoff retry logic for data downloader from yfinance

### 2026-08-10 — Landing Page & Marketing Site
- Created professional dark-themed landing page as the new home route (`/`)
- Moved existing dashboard application to `/app` route
- Landing page features: hero section, feature cards, product showcase, strategy grid, comparison section, benchmark highlight
- Integrated app screenshots for all sections
- Dashboard title now links back to landing page

### 2026-08-07 — Architecture, DevOps & API Production Hardening
- Refactored data and service layers to use dependency injection, decoupling business logic from Flask framework
- Added environment-based configuration system for development and production settings
- Added Docker support for containerized deployment
- Added GitHub Actions CI/CD pipeline for automated testing on every commit
- Added rate limiting to API endpoints (5 requests per minute) with custom error handler
- Added request/response logging with execution time tracking for all API requests
- Simplified test infrastructure by removing Flask dependencies from data layer tests

### 2026-08-06 — Advanced Charting
- Price chart now renders OHLC data as candlesticks instead of a simple close-price line
- Dropdown to switch between Candlestick, Line (Open/High/Low/Close) views; preference persisted in localStorage
- Strategies now return structured `StrategyOutput` with indicator metadata (display type, subplot assignment, y-axis range)
- RSI and MACD rendered in separate subplots below the main price panel with linked x-axes and fixed y-ranges where applicable

### 2026-08-05 — Fixed Amount Take-Profit & Backend-Driven Charts
- Added fixed-amount take-profit rule and extended the take-profit framework
- Refactored chart rendering to be backend-driven; frontend now renders semantic chart specs
- Price chart supports toggling between signal and execution markers (buy, sell, stop-loss, take-profit)
- Added chart serializer and renderer modules with coverage tests

### 2026-08-03 — Take-Profit Framework
- Added configurable take-profit exits that lock in gains once a target price is reached
- Integrated take-profit controls into the risk management panel
- Extended backtest results to distinguish take-profit exits from strategy signal exits

### 2026-07-31 — Advanced Stop-Loss Rules
- Added fixed-price-offset and trailing stop-loss options for more flexible downside protection
- Trailing stop tracks the highest price since entry, letting winners run while protecting gains

### 2026-07-30 — Pluggable Stop-Loss Framework
- Replaced hard-coded stop-loss handling with an extensible registry so new stop-loss rules can be added without touching core code
- UI stop-loss selection now uses a dynamic dropdown with per-rule parameter fields

### 2026-07-29 — Stop-Loss Risk Support
- Added optional stop-loss configuration to backtests with automatic exit logic
- Trade history now records the exit reason, making it clear when a stop-loss triggered

### 2026-07-28 — Compare Tab Form Persistence
- Added form persistence for the Compare tab via localStorage

### 2026-07-27 — Strategy Comparison Tab
- Added Strategy Comparison Tab for running 2–6 strategies side-by-side on the same ticker and date range
- Comparison dashboard with metrics matrix (best-value highlighting), overlaid equity and drawdown charts, and per-strategy trade history tabs
- Added `POST /compare` API endpoint with per-strategy error isolation

### 2026-07-24 — Market Data Caching
- Added local SQLite database for caching downloaded market data
- Cache-first retrieval eliminates redundant Yahoo Finance API calls across repeated backtests
- Automatic range merging consolidates overlapping cached date ranges

### 2026-07-22 — Dashboard UI Overhaul & KPI Interpretation System
- Redesigned dashboard layout: compacted KPI grid, 3-column metrics, narrower sidebar
- Added backend KPI Interpreter module with dedicated `kpi_cards` response object
- KPI values are now color-coded based on interpretation levels (Excellent, Good, Average, Poor)
- Color coding applied to CAGR, Profit Factor, Sharpe Ratio, Sortino Ratio, Max Drawdown and Alpha
- Added hover tooltips on each KPI card with metric explanations and interpretation ranges

### 2026-07-20 — Benchmark Comparison & Extended Risk Metrics
- Added Buy & Hold benchmark comparison with passive equity curve overlay on the Equity Chart
- Added Benchmark Metrics panel displaying Buy & Hold Final Value, Buy & Hold Return, and Strategy Alpha
- Added Sortino Ratio and Calmar Ratio to Risk Metrics

### 2026-07-15 — Error Handling
- Added user-friendly error modal for frontend and backend validation errors

### 2026-07-14 — Loading Overlay
- Added full-screen loading overlay during backtest execution

### 2026-07-13 — RSI Strategy, Chart Interaction & Warm-up Fix
- Added trading strategy: RSI Mean Reversion
- Improved chart interaction: mouse-wheel zoom, drag to pan
- Added automatic indicator warm-up period for more accurate recursive indicator calculations
- Fixed bug where consecutive BUY/SELL signals generated via RSI Mean Reversion strategy were causing incorrect backtest results

### 2026-07-12 — Indicators & Strategy Expansion
- Added EMA, RSI and MACD indicators
- Added trading strategies: EMA Crossover, MACD Crossover

### 2026-07-10 — Frontend Dashboard
- Created a dashboard for triggering backtests and viewing analytics results
- Added interactive dashboard with Plotly charts (price, equity curve, drawdown) and trade history table
- Strategy parameters are now dynamically rendered from a central registry

### 2026-07-09 — Serialization Fix
- Fixed a bug in JSON serialization of NaN values

### 2026-07-08 — Backtest Service & API
- Added backtest service layer for orchestration of the backtest workflow
- Added `POST /backtest` REST API endpoint with JSON request/response

### 2026-07-04 — Analytics Engine
- Added Analytics Engine with portfolio metrics, risk metrics, and trade statistics

### 2026-07-01 — Portfolio Simulator
- Added Portfolio Simulator for trade lifecycle execution with configurable initial capital

### 2026-07-01 — Data Module, Indicator Engine & Strategy Engine
- Added Market Data module for downloading and cleaning historical stock data via Yahoo Finance
- Added generic Indicator Engine with SMA indicator implementation
- Added Strategy Engine with SMA Crossover strategy

### 2026-06-30 — Project setup and initial commit
- Added basic flask project structure and API blueprint
- Added logging module
