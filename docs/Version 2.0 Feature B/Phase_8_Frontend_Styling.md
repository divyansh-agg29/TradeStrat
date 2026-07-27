# Phase 8 — Frontend Styling

## Objective

Populate `frontend/static/css/compare.css` with all styles needed for the Compare tab: tab bar, compare control panel, strategy entry form, metrics matrix, trade history tabs, and overall layout. This phase ensures the Compare tab has a polished, consistent look matching the existing Backtest tab's dark theme.

---

## Scope

### Modified Files

#### `frontend/static/css/compare.css`

This file was created as an empty shell in Phase 5. Now populate it with the following style sections.

---

## Style Sections

### 1. Tab Bar

```css
#tab-bar {
    display: flex;
    gap: 0;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 0 1rem;
}

.tab-btn {
    padding: 0.75rem 1.5rem;
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 0.95rem;
    font-weight: 500;
    transition: color 0.2s, border-bottom-color 0.2s;
}

.tab-btn.active {
    color: var(--text-primary);
    border-bottom-color: var(--accent);
}

.tab-btn:hover {
    color: var(--text-primary);
}
```

### 2. Tab Content Visibility

```css
.tab-content {
    display: none;
}

.tab-content.active {
    display: block;
}
```

### 3. Compare Container Layout

Mirror the existing `#app-container` layout (sidebar + main area):

```css
#compare-container {
    display: flex;
    gap: 1.5rem;
    padding: 1.5rem;
    max-width: 1600px;
    margin: 0 auto;
}

#compare-control-panel {
    width: 280px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

#compare-dashboard {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    min-width: 0;
}
```

### 4. Strategy Entry Blocks

```css
.compare-strategy-entry {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.75rem;
    margin-bottom: 0.75rem;
}

.compare-strategy-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.compare-strategy-label {
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--text-primary);
}

.compare-remove-btn {
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0 0.25rem;
    line-height: 1;
    transition: color 0.2s;
}

.compare-remove-btn:hover {
    color: var(--danger, #F44336);
}

.compare-remove-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
}

.compare-strategy-params {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
```

### 5. Add Strategy Button

```css
#add-strategy-btn {
    width: 100%;
    padding: 0.5rem;
    margin-top: 0.25rem;
    border: 1px dashed var(--border);
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    border-radius: 4px;
    font-size: 0.85rem;
    transition: color 0.2s, border-color 0.2s;
}

#add-strategy-btn:hover {
    color: var(--accent);
    border-color: var(--accent);
}

#add-strategy-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
}
```

### 6. Summary Header

```css
.compare-summary {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    padding: 1rem 1.25rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 0.9rem;
    color: var(--text-secondary);
}

.compare-summary strong {
    color: var(--text-primary);
}
```

### 7. Metrics Comparison Matrix

```css
#compare-matrix-container {
    overflow-x: auto;
}

#compare-matrix-container table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
}

#compare-matrix-container thead th {
    padding: 0.6rem 0.75rem;
    text-align: center;
    font-weight: 600;
    color: var(--text-primary);
    border-bottom: 2px solid var(--border);
    white-space: nowrap;
}

#compare-matrix-container thead th:first-child {
    text-align: left;
}

#compare-matrix-container tbody td {
    padding: 0.5rem 0.75rem;
    text-align: center;
    color: var(--text-secondary);
    border-bottom: 1px solid var(--border);
}

#compare-matrix-container tbody td:first-child {
    text-align: left;
    font-weight: 500;
    color: var(--text-primary);
}

#compare-matrix-container tbody tr:hover {
    background: rgba(255, 255, 255, 0.03);
}

/* Best value highlight */
.compare-best {
    background: rgba(76, 175, 80, 0.15);
    color: #4CAF50;
    font-weight: 600;
}

/* Error cell */
.compare-error {
    color: var(--danger, #F44336);
    font-style: italic;
}
```

### 8. Trade History Tabs

```css
#compare-trades-tabs {
    display: flex;
    gap: 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1rem;
    overflow-x: auto;
}

.compare-trade-tab {
    padding: 0.5rem 1rem;
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 0.8rem;
    white-space: nowrap;
    transition: color 0.2s, border-bottom-color 0.2s;
}

.compare-trade-tab.active {
    color: var(--text-primary);
    border-bottom-color: var(--accent);
}

.compare-trade-tab:hover {
    color: var(--text-primary);
}

.compare-trade-content {
    display: none;
}

.compare-trade-content.active {
    display: block;
}

.compare-trade-error {
    padding: 1rem;
    color: var(--danger, #F44336);
    font-style: italic;
}
```

### 9. Responsive Adjustments

```css
@media (max-width: 900px) {
    #compare-container {
        flex-direction: column;
    }

    #compare-control-panel {
        width: 100%;
    }
}
```

---

## CSS Variables Referenced

These variables should already be defined in `theme.css`. If any are missing, add them:

| Variable | Typical Value | Description |
|----------|---------------|-------------|
| `--surface` | `#1e1e2e` | Card/panel background |
| `--border` | `#2d2d3d` | Border color |
| `--text-primary` | `#e0e0e0` | Primary text |
| `--text-secondary` | `#a0a0a0` | Secondary text |
| `--accent` | `#2196F3` | Accent/highlight color |
| `--danger` | `#F44336` | Error/danger color (may need to add) |

---

## Verification

After this phase, the full feature is complete:

1. Tab bar looks clean with proper active/hover states.
2. Compare control panel matches the Backtest panel's visual style.
3. Strategy entry blocks have clear boundaries, proper spacing, and working remove buttons.
4. Metrics matrix is readable with proper alignment, row highlighting on hover, and green best-value cells.
5. Charts are properly sized within the dashboard layout.
6. Trade history tabs switch correctly with proper active styling.
7. Responsive layout stacks on narrow viewports.
8. No visual regressions on the existing Backtest tab.

---

## Final Checklist — Full Feature Complete

After all 8 phases:

- [ ] Models: `ComparisonRequest`, `StrategyResult`, `ComparisonResult` exist and are exported.
- [ ] Service: `run_comparison` orchestrates sequential backtests with error isolation.
- [ ] Serializer: `serialize_comparison_result` strips KPI cards and benchmark per strategy, extracts benchmark to top level.
- [ ] API: `POST /compare` endpoint parses, executes, serializes, returns JSON.
- [ ] Tab System: Two tabs switch between Backtest and Compare views.
- [ ] Compare Form: 2–6 strategies with add/remove, dynamic params, validation.
- [ ] Results: Summary, metrics matrix, equity overlay + benchmark, drawdown overlay, trade tabs.
- [ ] Styling: All compare elements styled consistently with existing theme.
- [ ] All existing tests pass.
- [ ] All new tests pass.
- [ ] Existing Backtest tab unchanged.

---

## Dependencies

- Phase 5 (Tab System) — tab bar and content containers must exist.
- Phase 6 (Compare Form) — form elements must exist for styling.
- Phase 7 (Results Rendering) — result sections must exist for styling.

## Depended On By

- None. This is the final phase.
