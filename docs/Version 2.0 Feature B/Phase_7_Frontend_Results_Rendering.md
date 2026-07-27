# Phase 7 — Frontend Results Rendering

## Objective

Implement the `renderComparisonResults(data)` function that takes the `POST /compare` response data and renders the comparison dashboard: summary header, metrics comparison matrix, equity curve overlay chart (with benchmark), drawdown comparison chart, and per-strategy trade history tabs.

---

## Scope

### Modified Files

#### `frontend/templates/index.html`

Add result section containers inside `<main id="compare-dashboard">`:

```html
<main id="compare-dashboard">

    <!-- Summary Header -->
    <section id="compare-summary-section">
    </section>

    <!-- Metrics Matrix -->
    <section id="compare-matrix-section" class="dashboard-panel">
        <div class="section-header">
            <h2>Metrics Comparison</h2>
        </div>
        <div id="compare-matrix-container"></div>
    </section>

    <!-- Equity Curve Overlay -->
    <section id="compare-equity-section" class="chart-panel">
        <div class="section-header">
            <h2>Equity Curves</h2>
        </div>
        <div id="compare-equity-chart" class="chart-container"></div>
    </section>

    <!-- Drawdown Comparison -->
    <section id="compare-drawdown-section" class="chart-panel">
        <div class="section-header">
            <h2>Drawdown Comparison</h2>
        </div>
        <div id="compare-drawdown-chart" class="chart-container"></div>
    </section>

    <!-- Trade History (Tabbed) -->
    <section id="compare-trades-section" class="dashboard-panel">
        <div class="section-header">
            <h2>Trade History</h2>
        </div>
        <div id="compare-trades-tabs"></div>
        <div id="compare-trades-content"></div>
    </section>

</main>
```

#### `frontend/static/js/compare.js`

Implement the rendering functions. Called from `onRunComparison()` after a successful API response.

---

## Rendering Functions

### `renderComparisonResults(data)`

Main entry point. Receives `data` from the API response (`data.common`, `data.benchmark`, `data.results`).

```javascript
function renderComparisonResults(data) {
    renderCompareSummary(data.common, data.results);
    renderCompareMatrix(data.results);
    renderCompareEquityChart(data.results, data.benchmark);
    renderCompareDrawdownChart(data.results);
    renderCompareTradeHistory(data.results);
}
```

---

### 1. `renderCompareSummary(common, results)`

Renders a compact summary header inside `#compare-summary-section`.

**Content:**
- Ticker: `common.ticker`
- Period: `common.start_date` to `common.end_date`
- Capital: formatted `common.initial_capital`
- Strategies: `N total, X successful, Y failed`

**HTML output example:**

```html
<div class="compare-summary">
    <span><strong>RELIANCE.NS</strong></span>
    <span>2020-01-01 → 2024-12-31</span>
    <span>Capital: ₹1,00,000</span>
    <span>3 strategies: 2 successful, 1 failed</span>
</div>
```

---

### 2. `renderCompareMatrix(results)`

Builds an HTML table inside `#compare-matrix-container`.

**Strategy label generation:**

For each result, generate a column header from `result.strategy`:
- Use the `STRATEGY_REGISTRY[type].label` for the display name.
- Append a short parameter summary in parentheses.
- Examples: `"SMA Crossover (20/50)"`, `"RSI MR (14, 30/70)"`.

```javascript
function getStrategyLabel(strategy) {
    const reg = STRATEGY_REGISTRY[strategy.type];
    const label = reg ? reg.label : strategy.type;
    const paramValues = Object.values(strategy.parameters).join("/");
    return label + " (" + paramValues + ")";
}
```

**Metrics rows:**

| Row Label | Source Object | Source Field | Format |
|-----------|-------------|-------------|--------|
| CAGR | `portfolio_metrics` | `cagr` | percentage |
| Total Return | `portfolio_metrics` | `total_return` | percentage |
| Sharpe Ratio | `risk_metrics` | `sharpe_ratio` | number |
| Sortino Ratio | `risk_metrics` | `sortino_ratio` | number |
| Max Drawdown | `risk_metrics` | `maximum_drawdown` | percentage |
| Win Rate | `trade_metrics` | `win_rate` | percentage |
| Profit Factor | `trade_metrics` | `profit_factor` | number |
| Total Trades | `trade_metrics` | `total_trades` | integer |

**Define this as a constant array:**

```javascript
const COMPARE_METRICS = [
    { label: "CAGR", source: "portfolio_metrics", field: "cagr", format: "percentage", higherIsBetter: true },
    { label: "Total Return", source: "portfolio_metrics", field: "total_return", format: "percentage", higherIsBetter: true },
    { label: "Sharpe Ratio", source: "risk_metrics", field: "sharpe_ratio", format: "number", higherIsBetter: true },
    { label: "Sortino Ratio", source: "risk_metrics", field: "sortino_ratio", format: "number", higherIsBetter: true },
    { label: "Max Drawdown", source: "risk_metrics", field: "maximum_drawdown", format: "percentage", higherIsBetter: false },
    { label: "Win Rate", source: "trade_metrics", field: "win_rate", format: "percentage", higherIsBetter: true },
    { label: "Profit Factor", source: "trade_metrics", field: "profit_factor", format: "number", higherIsBetter: true },
    { label: "Total Trades", source: "trade_metrics", field: "total_trades", format: "integer", higherIsBetter: true },
];
```

**Best-value highlighting:**

For each row, find the best value among successful strategies:
- If `higherIsBetter` is true → highest value wins.
- If `higherIsBetter` is false (Max Drawdown) → lowest absolute value wins.
- Apply CSS class `compare-best` to the winning cell.
- Failed strategies show "Error" and are excluded from comparison.

**Table generation logic:**

```
1. Create <table> with <thead> and <tbody>.
2. <thead>: first column empty, then one <th> per strategy with label.
3. For each metric in COMPARE_METRICS:
   a. Create <tr> with metric label in first <td>.
   b. For each result:
      - If result.success: extract value from result[source][field], format it.
      - If !result.success: show "Error".
   c. Find best value index, add "compare-best" class to that <td>.
4. Insert table into #compare-matrix-container.
```

---

### 3. `renderCompareEquityChart(results, benchmark)`

Renders a Plotly chart in `#compare-equity-chart`.

**Strategy traces:**

For each successful result:
- X: dates from `result.portfolio_history` (the `date` field of each entry).
- Y: portfolio values from `result.portfolio_history` (the `portfolio_value` or equivalent field).
- Name: strategy label (from `getStrategyLabel`).
- Color: from the strategy color palette by index.
- Line style: solid.

**Benchmark trace:**

If `benchmark` is not null:
- X: dates from `benchmark.portfolio_history`.
- Y: values from `benchmark.portfolio_history`.
- Name: "Buy & Hold".
- Color: grey (`#9E9E9E`).
- Line style: **dotted** (`dash: "dot"`).

**Color palette:**

```javascript
const STRATEGY_COLORS = [
    "#2196F3",  // Blue
    "#FF9800",  // Orange
    "#4CAF50",  // Green
    "#F44336",  // Red
    "#9C27B0",  // Purple
    "#009688",  // Teal
];
```

**Plotly layout:**

```javascript
{
    xaxis: { title: "Date" },
    yaxis: { title: "Portfolio Value" },
    legend: { orientation: "h", y: -0.2 },
    template: "plotly_dark",  // or match existing chart theme
}
```

---

### 4. `renderCompareDrawdownChart(results)`

Renders a Plotly chart in `#compare-drawdown-chart`.

For each successful result:
- X: dates from `result.analytics_history`.
- Y: drawdown values from `result.analytics_history` (the `drawdown` field).
- Name: strategy label.
- Color: from palette by index.

No benchmark trace on the drawdown chart.

**Plotly layout:**

```javascript
{
    xaxis: { title: "Date" },
    yaxis: { title: "Drawdown (%)" },
    legend: { orientation: "h", y: -0.2 },
}
```

---

### 5. `renderCompareTradeHistory(results)`

Renders a tabbed trade history section.

**Tab buttons:**

Inside `#compare-trades-tabs`, create one button per strategy:

```html
<button class="compare-trade-tab active" data-index="0">SMA (20/50)</button>
<button class="compare-trade-tab" data-index="1">EMA (12/26)</button>
<button class="compare-trade-tab" data-index="2">RSI MR (14, 30/70)</button>
```

**Tab content:**

Inside `#compare-trades-content`, create one div per strategy (hidden by default, first one visible):

- For successful strategies: render the same trade history table as the existing Backtest tab. Columns: Entry Date, Exit Date, Holding Period, Entry Price, Exit Price, Quantity, Investment, Exit Value, Return %, Profit/Loss.
- For failed strategies: show the error message.

**Tab switching:**

Clicking a tab button shows the corresponding content div and hides others.

---

## Handling Edge Cases in Rendering

| Scenario | Behavior |
|----------|----------|
| All strategies succeed | Matrix fully populated, all chart traces visible. |
| Some strategies fail | "Error" in matrix cells for failed columns. Failed strategies omitted from charts. Error message in trade tab. |
| All strategies fail | Matrix shows all "Error". Charts empty (no traces). All trade tabs show errors. Benchmark is null — no benchmark trace. |
| Strategy has 0 trades but succeeds | Metrics populated (may show 0 trades, 0% win rate). Equity chart shows flat line. Trade history table empty. |

---

## Verification

After this phase:

1. Run a comparison with 2–3 strategies via the Compare tab.
2. Summary header shows correct common parameters and success/fail counts.
3. Metrics matrix shows all 8 metric rows with correct values and best-value highlighting.
4. Equity curve chart shows one colored trace per successful strategy + dotted grey benchmark.
5. Drawdown chart shows one trace per successful strategy.
6. Trade history tabs work — clicking each tab shows that strategy's trades.
7. Intentionally include a bad strategy to verify error handling in matrix, charts, and trade tabs.

---

## Dependencies

- Phase 5 (Tab System) — Compare tab container must exist.
- Phase 6 (Compare Form) — `onRunComparison` must call `renderComparisonResults(data)`.
- Phases 1–4 (Backend) — API response must be live.
- Existing `formatters.js` — `formatByType` used for metric formatting.
- Existing `strategies.js` — `STRATEGY_REGISTRY` used for strategy labels.

## Depended On By

- Phase 8 (Styling) — styles the matrix, charts, trade tabs.
