# Phase 6 — Frontend Compare Form

## Objective

Build the comparison configuration form inside the Compare tab's control panel. Users can configure shared parameters (ticker, dates, capital), add/remove 2–6 strategy entries with dynamic parameter inputs, validate inputs, and submit a comparison request to `POST /compare`.

---

## Scope

### Modified Files

#### `frontend/templates/index.html`

Replace the placeholder content inside `#compare-container` (added in Phase 5) with the compare layout:

```html
<div id="compare-container">

    <!-- Compare Control Panel -->
    <aside id="compare-control-panel">

        <h2>Compare Strategies</h2>

        <!-- Shared Parameters -->
        <section class="panel">
            <h3>Configuration</h3>

            <div class="form-group">
                <label for="compare-ticker">Ticker</label>
                <input type="text" id="compare-ticker" class="form-input" placeholder="RELIANCE.NS">
            </div>

            <div class="form-group">
                <label for="compare-start-date">Start Date</label>
                <input type="date" id="compare-start-date" class="form-input">
            </div>

            <div class="form-group">
                <label for="compare-end-date">End Date</label>
                <input type="date" id="compare-end-date" class="form-input">
            </div>

            <div class="form-group">
                <label for="compare-capital">Initial Capital</label>
                <input type="number" id="compare-capital" class="form-input" value="100000">
            </div>
        </section>

        <!-- Strategy List -->
        <section class="panel">
            <h3>Strategies</h3>

            <div id="compare-strategy-list">
                <!-- Strategy entries dynamically inserted here -->
            </div>

            <button id="add-strategy-btn" class="btn-secondary">+ Add Strategy</button>
        </section>

        <!-- Execute -->
        <section class="panel">
            <button id="run-comparison-btn" class="btn-primary">Run Comparison</button>
        </section>

    </aside>

    <!-- Compare Results Area (Phase 7) -->
    <main id="compare-dashboard">
        <!-- Populated by Phase 7 -->
    </main>

</div>
```

#### `frontend/static/js/compare.js`

Implement the form management logic:

**1. Strategy entry management:**

```javascript
// State: array of strategy entry data
let compareStrategies = [];
const MIN_STRATEGIES = 2;
const MAX_STRATEGIES = 6;
```

**`addStrategyEntry()`** — Adds a new strategy block to `#compare-strategy-list`:
- Creates a container div with class `compare-strategy-entry`.
- Adds a header row with "Strategy #N" label and a "Remove" button.
- Adds a strategy type dropdown (populated from `STRATEGY_REGISTRY` keys, same as existing single-backtest dropdown).
- Adds a dynamic parameters container that updates when the dropdown changes.
- Appends to `#compare-strategy-list`.
- Updates button states.

**`removeStrategyEntry(index)`** — Removes a strategy block:
- Removes the DOM element.
- Updates the numbering on remaining entries.
- Updates button states.

**`updateButtonStates()`** — Enforces min/max:
- Disable "Add Strategy" when count >= 6.
- Disable all "Remove" buttons when count <= 2.

**`onCompareStrategyTypeChanged(entryIndex)`** — When dropdown changes:
- Clear the parameters container for that entry.
- Look up the new strategy type in `STRATEGY_REGISTRY`.
- Render parameter inputs with defaults (reuse the same parameter definitions from `strategies.js`).

**2. Initialization:**

```javascript
function initCompareForm() {
    // Add 2 default strategy entries
    addStrategyEntry();
    addStrategyEntry();

    // Event listeners
    document.getElementById("add-strategy-btn")
        .addEventListener("click", addStrategyEntry);

    document.getElementById("run-comparison-btn")
        .addEventListener("click", onRunComparison);
}
```

Call `initCompareForm()` from `app.js` inside `initializeApplication()`.

**3. Collecting form data:**

```javascript
function collectComparisonRequest() {
    return {
        ticker: document.getElementById("compare-ticker").value.trim(),
        start_date: document.getElementById("compare-start-date").value,
        end_date: document.getElementById("compare-end-date").value,
        initial_capital: parseFloat(document.getElementById("compare-capital").value),
        risk_free_rate: 0.0,
        strategies: collectStrategyConfigs(),
    };
}
```

**`collectStrategyConfigs()`** — Iterates over all `.compare-strategy-entry` elements, reads each dropdown value and parameter inputs, returns an array of `{ type, parameters }` objects.

**4. Validation:**

```javascript
function validateComparisonRequest(request) {
    const errors = [];

    if (!request.ticker) errors.push("Ticker is required.");
    if (!request.start_date) errors.push("Start date is required.");
    if (!request.end_date) errors.push("End date is required.");
    if (request.start_date >= request.end_date) errors.push("Start date must be before end date.");

    // Per-strategy validation
    request.strategies.forEach(function(s, i) {
        const registry = STRATEGY_REGISTRY[s.type];
        if (registry && registry.validate) {
            const stratErrors = registry.validate(s.parameters);
            stratErrors.forEach(function(e) {
                errors.push("Strategy " + (i + 1) + ": " + e);
            });
        }
    });

    return errors;
}
```

**5. Submission:**

```javascript
async function onRunComparison() {
    const request = collectComparisonRequest();

    // Validate
    const errors = validateComparisonRequest(request);
    if (errors.length > 0) {
        showErrorModal("Validation Error", errors.join("\n"));
        return;
    }

    // Show loading overlay
    showLoading("Running Comparison...");

    try {
        const response = await fetch("/compare", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(request),
        });

        const result = await response.json();

        if (!result.success) {
            showErrorModal(result.error.type, result.error.message);
            return;
        }

        // Phase 7: renderComparisonResults(result.data);

    } catch (err) {
        showErrorModal("Network Error", err.message);
    } finally {
        hideLoading();
    }
}
```

The `renderComparisonResults` call is stubbed as a comment — it will be implemented in Phase 7.

---

## Strategy Entry HTML Structure (Generated by JS)

Each entry rendered by `addStrategyEntry()`:

```html
<div class="compare-strategy-entry" data-index="0">

    <div class="compare-strategy-header">
        <span class="compare-strategy-label">Strategy 1</span>
        <button class="compare-remove-btn" title="Remove">&times;</button>
    </div>

    <div class="form-group">
        <label>Strategy Type</label>
        <select class="form-select compare-strategy-type">
            <option value="sma_crossover">SMA Crossover</option>
            <option value="ema_crossover">EMA Crossover</option>
            <option value="macd_crossover">MACD Crossover</option>
            <option value="rsi_mean_reversion">RSI Mean Reversion</option>
        </select>
    </div>

    <div class="compare-strategy-params">
        <!-- Dynamic parameter inputs based on selected strategy type -->
    </div>

</div>
```

---

## Interaction Details

| Action | Behavior |
|--------|----------|
| Page loads | Two default strategy entries shown (both SMA Crossover with defaults). |
| Click "Add Strategy" | New entry appended. Max 6. Button disabled at 6. |
| Click "Remove" (×) | Entry removed. Remaining entries renumbered. Disabled at 2. |
| Change strategy dropdown | Parameters area clears and re-renders with new strategy's inputs and defaults. |
| Click "Run Comparison" | Validates → shows loading → calls `POST /compare` → hides loading → renders results (Phase 7). |
| Validation error | Error modal with list of issues. No API call made. |

---

## Verification

After this phase:

1. Switching to the Compare tab shows the form with 2 default strategy entries.
2. Add/remove buttons work and respect 2–6 limits.
3. Changing a strategy type updates the parameter inputs dynamically.
4. Clicking "Run Comparison" with valid inputs calls `POST /compare` and receives a response (results rendering is a stub — just check browser Network tab).
5. Clicking "Run Comparison" with invalid inputs shows the error modal.
6. Existing Backtest tab works exactly as before.

---

## Dependencies

- Phase 5 (Tab System) — `#compare-container` must exist in the DOM.
- Phases 1–4 (Backend) — `POST /compare` endpoint must be live for the API call.
- Existing `strategies.js` — `STRATEGY_REGISTRY` is used for dropdown options and parameter definitions.
- Existing `error-modal.js` — `showErrorModal` is used for validation errors.
- Existing `loading.js` — `showLoading`, `hideLoading` are used.

## Depended On By

- Phase 7 (Results Rendering) — uses the submitted request data and renders results.
- Phase 8 (Styling) — styles the form elements.
