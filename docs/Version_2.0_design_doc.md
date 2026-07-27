# Multi-Strategy Comparison, Data Caching, and Report Exporting - Design Proposal

## Overview

Version 2.0 introduces three major capabilities that transform the platform from a single-run backtesting tool into a comprehensive strategy research environment:

1. **Strategy Comparison Tab** — Run multiple strategies on the same market conditions and compare their performance side-by-side.
2. **Market Data Caching** — Cache historical market data locally to eliminate redundant downloads and accelerate multi-strategy comparisons.
3. **Report Exporting** — Export backtest results and comparison outputs as structured reports for sharing and archival.

These features work together: caching accelerates the multiple backtests required for comparison, and report exporting provides a clean output format for the analysis results.

---

# Feature 1: Strategy Comparison Tab

## Objectives

The Strategy Comparison Tab enables users to run multiple trading strategies on the same ticker, date range, and initial capital, then visualize and analyze their relative performance in a unified interface.

Key goals:

- Compare 2–6 strategies simultaneously.
- Visualize equity curves overlaid for direct performance comparison.
- Present KPI metrics in a matrix format for quick scanning.
- Highlight the best-performing strategy for each metric.
- Allow users to select a primary objective metric for ranking.

## Expected Behavior

### Input Configuration

Users configure a comparison run by specifying:

- **Common parameters** (shared across all strategies):
  - Ticker symbol
  - Start date and end date
  - Initial capital
  - Risk-free rate

- **Strategy list** (2–6 strategies):
  - Strategy type (e.g., SMA Crossover, EMA Crossover, RSI Mean Reversion, MACD Crossover)
  - Strategy-specific parameters for each entry

The configuration interface should allow adding/removing strategy entries and editing individual strategy parameters independently.

### Execution

When the user initiates the comparison:

- The system executes one backtest per strategy in the list.
- All backtests use identical market data (ticker + date range) to ensure fair comparison.
- Execution may be sequential or parallel (parallel preferred for performance).
- A progress indicator shows which strategy is currently running.

### Output Display

The comparison results are presented in a dedicated tab or view containing:

#### 1. Summary Header

- Ticker, date range, initial capital, risk-free rate
- Number of strategies compared
- Primary objective metric (user-selectable)
- Overall winner badge on the best-performing strategy (based on primary objective)

#### 2. KPI Comparison Matrix

A table where:

- **Rows**: Key performance metrics (CAGR, Sharpe Ratio, Sortino Ratio, Max Drawdown, Alpha, Total Return, Win Rate, Profit Factor, Total Trades)
- **Columns**: Each strategy in the comparison
- **Cells**: The metric value for that strategy
- **Highlighting**: The best value in each row is visually highlighted (green border or subtle background color)

For metrics where lower is better (e.g., Max Drawdown), the lowest value is highlighted as best.

#### 3. Equity Curve Overlay Chart

A single Plotly chart showing:

- Equity curves for all strategies overlaid
- Each strategy assigned a distinct color
- Legend identifying each strategy
- Buy & Hold benchmark curve (if enabled)
- Interactive zoom/pan as in existing charts

#### 4. Drawdown Comparison Chart

A multi-line chart showing drawdown curves for all strategies overlaid, allowing users to compare risk profiles.

#### 5. Trade History Table (Optional)

A tabbed or expandable section showing trade history for each strategy, possibly with tabs to switch between strategies.

### Primary Objective Selection

Users can select a primary objective metric from a dropdown:

- CAGR
- Sharpe Ratio
- Sortino Ratio
- Max Drawdown (inverted)
- Alpha

The selected metric determines:
- Which strategy receives the overall “Winner” badge
- The default sorting order if a ranked table view is added later

This selection does not change the KPI matrix highlighting (which always shows best per row) — it only affects the overall winner badge.

## Constraints and Edge Cases

### Strategy Count Limits

- Minimum: 2 strategies (comparison requires at least two)
- Maximum: 6 strategies (to maintain UI readability and performance)
- UI should enforce these limits with validation messages

### Parameter Variability

- Strategies may have completely different parameters (e.g., SMA Crossover uses periods; RSI uses threshold and period)
- The configuration form must dynamically render the correct parameter inputs per strategy type
- No requirement to compare parameters across strategies — they are independent

### Execution Time

- Running 3–6 backtests sequentially may take 10–60 seconds depending on date range
- Progress indication is mandatory to avoid user confusion
- Parallel execution (if implemented) should respect rate limits on data fetching

### Data Consistency

- All strategies in a comparison must use the exact same market data snapshot
- If the market data download fails for one strategy, all strategies in the comparison should fail or retry
- Caching (Feature 2) ensures data consistency by reusing the same cached dataset

### Empty or Failed Results

- If a strategy backtest fails (e.g., no trades generated), its results should still appear in the comparison with placeholder values (N/A or appropriate indicators)
- The UI should handle missing data gracefully without breaking the matrix or charts

## Architectural Considerations

### API Contract

The comparison feature requires a new API endpoint that accepts:

- A list of strategy configurations
- Common parameters (ticker, dates, capital, risk-free rate)

And returns:

- An array of backtest results (one per strategy)
- Each result contains the same structure as the current single-strategy response

### Frontend State Management

- The comparison configuration (strategy list + parameters) should be persisted in localStorage
- Results should be stored in memory during the session
- No requirement to persist comparison results across page reloads initially

### Chart Rendering

- Existing Plotly chart infrastructure can be reused
- Multi-line charts require adding multiple trace objects instead of one
- Color palette should be extended to support 6 distinct strategy colors

---

# Feature 2: Market Data Caching

## Objectives

Eliminate redundant market data downloads by caching historical data locally in a database. This reduces latency, avoids hitting Yahoo Finance rate limits, and accelerates multi-strategy comparisons.

Key goals:

- Cache market data by ticker and date range.
- Serve cached data for subsequent requests with matching parameters.
- Provide a mechanism to invalidate or refresh cached data.
- Use a simple, serverless database (SQLite) that requires no external dependencies.

## Expected Behavior

### Cache Key

A cache entry is uniquely identified by:

- **Ticker symbol** (case-insensitive)
- **Start date**
- **End date**

If a user requests the same ticker and date range again, the system should serve the cached data instead of re-downloading.

### Cache Miss Handling

When a cache miss occurs:

- The system downloads data from Yahoo Finance as usual.
- The downloaded data is stored in the cache database.
- The data is returned to the caller.

### Cache Hit Handling

When a cache hit occurs:

- The system retrieves the data from the cache database.
- No external API call is made.
- The data is returned to the caller immediately.

### Cache Freshness

Users should have control over cache freshness:

- **Manual refresh option**: A button or UI control to force a fresh download for a specific ticker/date range.
- **Cache age display**: Optionally show when the cached data was last updated.
- **Cache invalidation**: A mechanism to clear the entire cache or specific entries.

### Cache Storage

The cache database should store:

- Ticker symbol
- Start date
- End date
- Last updated timestamp
- The full market data (OHLCV) in a serialized format (e.g., JSON or binary)

## Constraints and Edge Cases

### Date Range Overlap

If a user requests a date range that partially overlaps with cached data:

- **Option 1 (simpler)**: Treat as a cache miss and download the full range.
- **Option 2 (more complex)**: Merge cached and new data.

Given the complexity of merging, Option 1 is recommended for the initial implementation.

### Data Integrity

- Cached data must be validated before use (e.g., check for empty datasets, missing columns).
- If cached data is corrupted, treat as a cache miss and re-download.

### Database Growth

- The cache database will grow over time as users test different tickers and date ranges.
- A cleanup mechanism (e.g., delete entries older than 30 days) should be considered for a future iteration.
- Initial implementation may omit automatic cleanup.

### Concurrent Access

- SQLite handles concurrent reads well.
- Writes should be serialized to avoid database locking issues.
- A simple lock or queue mechanism may be needed if multiple backtests run in parallel.

## Architectural Considerations

### Database Schema

A simple table structure:

```sql
CREATE TABLE market_data_cache (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    last_updated TIMESTAMP NOT NULL,
    data_json TEXT NOT NULL,
    UNIQUE(ticker, start_date, end_date)
);
```

### Integration Point

Caching should be integrated at the **Data Service layer**:

- The `get_stock_data` function should first check the cache.
- If cache miss, call the downloader, store in cache, then return.
- This abstraction keeps caching transparent to the Backtest Service and Strategy Engine.

### Performance

- SQLite queries on a single table with a unique index will be very fast (<10ms).
- The primary bottleneck remains the initial download, which caching eliminates on subsequent runs.

### Testing

- Unit tests should verify:
  - Cache miss triggers download and storage.
  - Cache hit returns stored data without download.
  - Manual refresh forces download even with cache hit.
  - Corrupted cache data is handled gracefully.

---

# Feature 3: Report Exporting

## Objectives

Allow users to export backtest results (single or comparison) as structured reports for sharing, archival, or further analysis.

Key goals:

- Support JSON export (machine-readable, for re-import).
- Support Markdown export (human-readable, for documentation).
- Maintain consistency between single-strategy and comparison exports.
- Include all relevant metrics, charts, and configuration details.

## Expected Behavior

### Export Trigger

Export functionality should be accessible from:

- Single-strategy backtest results view
- Strategy comparison tab
- Possibly a global “Export” button in the UI

### Export Formats

#### JSON Export

Structure should mirror the API response:

- Configuration (ticker, dates, capital, risk-free rate, strategy parameters)
- Metrics (portfolio, risk, trade, benchmark)
- KPI cards
- Trade history
- Charts (optionally include data for re-rendering)

JSON export enables:

- Re-import into the platform for later viewing
- Integration with external tools or scripts
- Programmatic analysis

#### Markdown Export

A human-readable report containing:

- Header with configuration summary
- KPI metrics table
- Interpretation levels (color coding represented as text badges)
- Trade statistics summary
- Strategy parameters
- Optional: links or references to chart images

Markdown export enables:

- Documentation in version control
- Sharing in plain-text environments
- Conversion to HTML/PDF via external tools

### Comparison Export

When exporting a comparison:

- JSON should include an array of strategy results
- Markdown should present a comparison matrix similar to the UI
- Include which strategy won based on the primary objective metric

### File Naming

Exports should use descriptive filenames:

- Single strategy: `{ticker}_{strategy}_{start_date}_{end_date}.json|.md`
- Comparison: `{ticker}_comparison_{start_date}_{end_date}.json|.md`

## Constraints and Edge Cases

### Chart Data in Export

- Charts cannot be directly embedded in JSON or Markdown as images.
- Options:
  - **Exclude charts** (simplest, initial implementation)
  - **Include chart data** (Plotly JSON structure) for re-rendering
  - **Generate static images** (requires additional dependencies)

Initial implementation should exclude charts to avoid complexity.

### Large Trade History

- Trade history can be large (thousands of trades).
- JSON export should include full trade history.
- Markdown export should include a summary (total trades, win rate, profit factor) and optionally truncate the table.

### Comparison Complexity

- Comparison exports with 6 strategies can become lengthy.
- Markdown should use compact formatting (tables, not prose).
- JSON structure should remain flat and predictable.

## Architectural Considerations

### Backend Responsibility

- Export logic should live in a new `reporting` module.
- The module should accept a `BacktestResult` (or array for comparison) and return formatted strings (JSON or Markdown).
- This keeps export logic separate from serialization and API concerns.

### Frontend Responsibility

- The frontend triggers the export via a button click.
- The exported data can be:
  - **Generated client-side** from the already-loaded response data (simpler, no new API endpoint)
  - **Generated server-side** via a new API endpoint (more consistent with backend logic)

Client-side generation is recommended for the initial implementation since the data is already available in the browser.

### Future Extensions

- PDF export (requires a rendering library like `weasyprint` or `pdfkit`)
- HTML export (styled, self-contained report)
- Custom report templates
- Scheduled report generation (email reports)

---

# Cross-Feature Interactions

### Caching + Comparison

- Multi-strategy comparisons benefit directly from caching.
- With caching enabled, a comparison of 4 strategies on the same ticker/date range triggers only one download instead of four.
- This significantly reduces comparison execution time.

### Comparison + Exporting

- Comparison exports are a natural extension of single-strategy exports.
- The comparison matrix in the UI maps directly to the Markdown export table.
- JSON exports of comparisons enable batch analysis in external tools.

### Caching + Exporting

- Cached data includes the last updated timestamp.
- This timestamp can be included in exports to indicate data freshness.
- If a user exports a report using stale cached data, the timestamp provides transparency.

---

# Design Principles

The Version 2.0 features should adhere to the same architectural principles as the existing codebase:

- **Separation of concerns** — Caching belongs in the Data layer, comparison logic in the Service layer, export in a dedicated Reporting module.
- **Backend owns business logic** — Export formatting, cache validation, and comparison aggregation should be server-side where appropriate.
- **Frontend owns presentation** — The comparison tab UI, export triggers, and cache status display are frontend responsibilities.
- **Minimal external dependencies** — SQLite for caching (built-in), no new heavy libraries for exporting.
- **Progressive complexity** — Start with simple implementations (sequential execution, basic cache hit/miss, JSON/Markdown only) and enhance in future versions.

The overall goal is to make the platform more useful for strategy research by enabling faster, richer comparisons and providing clean output formats for sharing results.
