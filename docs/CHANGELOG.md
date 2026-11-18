
## Development Changelog

### 2026-11-18 — API Validation & Input Hardening
- Added `float()` casts for `initial_capital` and `risk_free_rate` in backtest parser to match comparison parser
- Added `initial_capital` validation in compare tab's `validateComparisonRequest()`
- Added `isinstance(strategy, dict)` type checks in both backtest and comparison parsers to return 400 instead of 500
- Added early validation for strategies list (must be a list with at least 2 entries) in comparison parser

### 2026-11-17 — Documentation, Logging & Polish

**Documentation & Logging**
- Fixed SETUP.md: corrected invalid JSON in health check example, removed misleading `flask run` suggestion, updated Python version to 3.13, added Docker env var documentation
- Added module-level docstrings to 11 files across `risk/`, `position_sizing/`, and `models/`
- Added debug logging to `risk/manager.py` and `position_sizing/manager.py` for rule resolution
- Removed 4 `console.log`/`console.error` calls from production JS (`api.js`, `ui.js`, `app.js`)

**Frontend**
- Added empty-state message for trade history table when no trades are executed
- Moved `<script>` tags inside `<body>` in `app.html` for valid HTML
- Namespaced error-modal global variables into single `errorModal` object

**Backend**
- Breakeven trades (`profit_loss == 0`) now counted as winning in analytics
- Removed unsupported `"5d"` and `"3mo"` from `_DAILY_OR_ABOVE` in `market_data_store.py`
- Added warning log when all strategies fail in comparison service
- Changed truthiness checks to explicit `is None` in `risk/config.py` and `position_sizing/config.py`

### 2026-11-16 — Code Quality, Cleanup & Test Improvements
**Code Quality**
- Fixed `BacktestRequest.strategy` type hint (`StrategyConfig` -> `StrategyConfig | None`) and added `None` guard on `strategy.type` in validation
- Standardized type hints to modern Python 3.10+ syntax (`X | None`, `list[X]`, `X | Y`) across 6 files; removed unused `typing` imports
- Replaced eager f-string formatting in `logger.debug()` calls with lazy `%s` formatting in `portfolio/simulator.py` hot loop
- Removed unused `import logging` from `comparison_service.py`
- Removed dead `start_date`/`end_date` assignments in `analytics/metrics.py`
- Deleted empty `utils/helpers.py` and `analytics/charts.py`
- Updated `.gitignore` with missing patterns (`.venv/`, `htmlcov/`, `coverage.xml`, `*.pyo`, `.DS_Store`, `Thumbs.db`); removed stale `.streamlit/`

**Test Infrastructure**
- Created shared `tests/api/conftest.py` (Flask `client` fixture) and `tests/strategy/helpers.py` (`create_market_data`); removed duplicates from 8 test files
- Added missing `__init__.py` in `tests/data/`, `tests/indicators/`, `tests/strategy/`
- Rewrote strategy registry tests to parametrize over all 5 strategies

**New Tests**
- Added interval annualization tests (`1h`, `1wk`) for CAGR, volatility, Sharpe, and finiteness
- Added non-zero `risk_free_rate` tests verifying Sharpe/Sortino decrease and portfolio metrics are unaffected
- Added unit tests for `_calculate_warmup_start()` covering daily/weekly/monthly warmup, intraday lookback clamping, and edge cases
- Added `match` patterns to all bare `pytest.raises()` calls across strategy, data validator, and position sizing tests

### 2026-11-15 — Robustness, Performance & API Hardening
**Frontend Cleanup & UX**
- Fixed `JSON.parse` crash on corrupt localStorage in `storage.js`
- Fixed `response.json()` crash on non-JSON error responses in `api.js` and `compare.js`
- Removed orphaned `index.html` template (dead code)
- Removed empty `charts.js` and `tables.js` files and their `<script>` tags
- Added required-field validation for dates in backtest tab
- Disabled Run Backtest / Run Comparison buttons during API requests to prevent duplicates
- Pinned Plotly CDN to v4.3.0 (was frozen at v1.58.5 via `plotly-latest`)

**Data Module**
- Refactored `_DB_CONN` global state with path validation, health checks, and `close_db()` cleanup
- Replaced row-by-row SQL inserts with `executemany()` and explicit transaction safety in `store_data()`

**Analytics & Backtest**
- Added zero-division guards in analytics for benchmark and CAGR calculations
- Added empty-DataFrame check after warm-up trimming with descriptive error message
- Eliminated double serialization in comparison response via caching

**API Hardening**
- Added `MAX_CONTENT_LENGTH` (1 MB) to reject oversized request payloads
- Added `ProxyFix` middleware so rate limiter uses real client IP behind reverse proxy



### 2026-11-14 — Security Hardening & Environment Configuration

**Environment & Configuration**
- Added `python-dotenv` with `.env.example` for environment variable management
- Fixed Docker running in debug mode by setting `APP_ENV=production` in Dockerfile
- Added debug-mode safety guard that prevents startup with `DEBUG=True` in production

**Docker & Deployment**
- Added `.env` to `.dockerignore` to prevent secrets leaking into image layers
- Replaced Flask dev server with Gunicorn as the production WSGI server
- Added configurable worker count via `WEB_WORKERS` env var (defaults to 2)
- Added non-root `appuser` to Dockerfile for least-privilege container execution



### 2026-08-20 — Kelly Criterion Position Sizing
- Added Kelly Criterion position sizing: calculates optimal position size from win rate, win/loss ratio, and a configurable Kelly fraction

### 2026-08-19 — Position Sizing Framework
- Added pluggable position sizing system with registry-based architecture (All-In, Fixed Percentage, Fixed Amount, Fixed Shares, Risk-Based)
- Position accumulation: consecutive BUY signals now add to the existing position instead of being ignored, with weighted average entry price tracking
- Integrated position sizing with the backtest service, API routes, and portfolio simulator
- Added frontend controls: enable checkbox, type dropdown, and dynamic parameter inputs in the sidebar
- Trade history table now displays an "Entries" column showing how many BUY entries composed each trade

### 2026-08-17 — Bollinger Bands Bounce strategy
- Added new BB Bounce trading strategy based on mean reversion
- Strategy generates BUY signals when price crosses below lower band and SELL signals when price crosses above upper band
- Integrated strategy into frontend with configurable period and std_multiplier parameters

### 2026-08-16 — Bollinger Bands indicator and speed optimisations
- Added new Bollinger Bands indicator in moving_average indicator module
- Significantly reduced runtime of backtest simulation

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

**Architecture**
- Refactored data and service layers to use dependency injection, decoupling business logic from Flask framework
- Added environment-based configuration system for development and production settings
- Simplified test infrastructure by removing Flask dependencies from data layer tests

**DevOps**
- Added Docker support for containerized deployment
- Added GitHub Actions CI/CD pipeline for automated testing on every commit

**API Hardening**
- Added rate limiting to API endpoints (5 requests per minute) with custom error handler
- Added request/response logging with execution time tracking for all API requests



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
