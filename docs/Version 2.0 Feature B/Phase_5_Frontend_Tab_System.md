# Phase 5 — Frontend Tab System

## Objective

Add a tab bar to the existing page with two tabs: "Backtest" (default) and "Compare". Switching tabs shows/hides the corresponding content areas. The existing single-backtest UI is wrapped inside the Backtest tab and remains completely unchanged. The Compare tab starts as an empty shell — its form and results are implemented in Phases 6 and 7.

---

## Scope

### Modified Files

#### `frontend/templates/index.html`

**1. Add a tab bar between the header and `#app-container`:**

```html
<!-- ================= TAB BAR ================= -->

<nav id="tab-bar">
    <button class="tab-btn active" data-tab="backtest">Backtest</button>
    <button class="tab-btn" data-tab="compare">Compare</button>
</nav>
```

Place this immediately after the closing `</header>` tag and before `<div id="app-container">`.

**2. Wrap the existing `#app-container` in a tab content div:**

The existing `<div id="app-container">` (which contains `<aside id="control-panel">` and `<main id="dashboard">`) becomes the content for the Backtest tab:

```html
<div id="backtest-tab-content" class="tab-content active">
    <div id="app-container">
        <!-- ... existing control panel and dashboard unchanged ... -->
    </div>
</div>
```

**3. Add the Compare tab content container (empty shell for now):**

```html
<div id="compare-tab-content" class="tab-content">
    <div id="compare-container">
        <!-- Phase 6: Compare control panel goes here -->
        <!-- Phase 7: Compare results area goes here -->
        <p style="padding: 2rem; color: var(--text-secondary);">
            Compare tab — coming soon.
        </p>
    </div>
</div>
```

**4. Add CSS link for compare styles (empty file for now, populated in Phase 8):**

In the `<head>` section, after the existing CSS links:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/compare.css') }}">
```

**5. Add JS script include for compare logic (empty file for now, populated in Phases 6–7):**

Before the closing `</body>`, alongside existing script includes:

```html
<script src="{{ url_for('static', filename='js/compare.js') }}"></script>
```

This must be included **before** `app.js` so that the tab initialization in `app.js` can reference functions defined in `compare.js`.

#### `frontend/static/js/app.js`

Add tab switching initialization inside `initializeApplication()`:

```javascript
function initializeApplication() {
    // ... existing initialization calls ...

    initTabSwitching();  // <-- Add this
}
```

**New function:**

```javascript
function initTabSwitching() {

    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    tabButtons.forEach(function(btn) {

        btn.addEventListener("click", function() {

            const targetTab = btn.dataset.tab;

            // Deactivate all tabs
            tabButtons.forEach(function(b) { b.classList.remove("active"); });
            tabContents.forEach(function(c) { c.classList.remove("active"); });

            // Activate selected tab
            btn.classList.add("active");
            document.getElementById(targetTab + "-tab-content").classList.add("active");

        });

    });

}
```

### New Files (Empty Shells)

#### `frontend/static/js/compare.js`

```javascript
"use strict";

// Compare tab logic — populated in Phases 6 and 7.
```

#### `frontend/static/css/compare.css`

```css
/* Compare tab styles — populated in Phase 8. */
```

---

## Tab Switching Behavior

| Action | Result |
|--------|--------|
| Page loads | Backtest tab active, Compare tab hidden. |
| Click "Compare" tab | Backtest content hidden, Compare content shown. Tab button styles update. |
| Click "Backtest" tab | Compare content hidden, Backtest content shown. |
| Run a backtest, then switch to Compare | Backtest results remain in DOM (not cleared). Switching back shows them. |
| Switching tabs does NOT trigger any API calls. |

---

## Minimal CSS Needed (in existing theme or compare.css)

```css
/* Tab bar */
#tab-bar {
    display: flex;
    gap: 0;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
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
}

.tab-btn.active {
    color: var(--text-primary);
    border-bottom-color: var(--accent);
}

.tab-btn:hover {
    color: var(--text-primary);
}

/* Tab content visibility */
.tab-content {
    display: none;
}

.tab-content.active {
    display: block;
}
```

Whether this goes into `compare.css` or an existing CSS file is a style decision — `compare.css` is the natural home.

---

## Verification

After this phase:

1. The page loads with the "Backtest" tab active and the existing dashboard visible.
2. Clicking "Compare" shows the placeholder text and hides the dashboard.
3. Clicking "Backtest" restores the dashboard.
4. Running a backtest in the Backtest tab works exactly as before.
5. No console errors.

---

## Dependencies

- Phases 1–4 (Backend) — should be complete, but this phase does not depend on them directly. Tab switching is pure frontend.

## Depended On By

- Phase 6 (Compare Form) — builds inside `#compare-container`.
- Phase 7 (Results Rendering) — builds inside `#compare-container`.
- Phase 8 (Styling) — styles the tab bar and compare content.
