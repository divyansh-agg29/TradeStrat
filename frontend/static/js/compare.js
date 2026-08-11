"use strict";

// Compare tab logic

const MIN_STRATEGIES = 2;
const MAX_STRATEGIES = 6;


// ── Initialization ───────────────────────────────────────────


function initCompareForm() {

    document.getElementById("add-strategy-btn")
        .addEventListener("click", addStrategyEntry);

    document.getElementById("run-comparison-btn")
        .addEventListener("click", onRunComparison);

    restoreCompareConfiguration();

}


// ── Strategy Entry Management ────────────────────────────────


function addStrategyEntry() {

    const list = document.getElementById("compare-strategy-list");
    const index = list.children.length;

    if (index >= MAX_STRATEGIES) {
        return;
    }

    const entry = document.createElement("div");
    entry.className = "compare-strategy-entry";
    entry.dataset.index = index;

    // Header
    const header = document.createElement("div");
    header.className = "compare-strategy-header";

    const label = document.createElement("span");
    label.className = "compare-strategy-label";
    label.textContent = "Strategy " + (index + 1);

    const removeBtn = document.createElement("button");
    removeBtn.className = "compare-remove-btn";
    removeBtn.title = "Remove";
    removeBtn.innerHTML = "&times;";
    removeBtn.addEventListener("click", function() {
        removeStrategyEntry(entry);
    });

    header.appendChild(label);
    header.appendChild(removeBtn);

    // Strategy type dropdown
    const typeGroup = document.createElement("div");
    typeGroup.className = "form-group";

    const typeLabel = document.createElement("label");
    typeLabel.textContent = "Strategy Type";

    const typeSelect = document.createElement("select");
    typeSelect.className = "form-select compare-strategy-type";

    for (const [key, strategy] of Object.entries(STRATEGY_REGISTRY)) {
        const option = document.createElement("option");
        option.value = key;
        option.textContent = strategy.label;
        typeSelect.appendChild(option);
    }

    typeSelect.addEventListener("change", function() {
        renderCompareStrategyParams(entry);
    });

    typeGroup.appendChild(typeLabel);
    typeGroup.appendChild(typeSelect);

    // Parameters container
    const paramsContainer = document.createElement("div");
    paramsContainer.className = "compare-strategy-params";

    entry.appendChild(header);
    entry.appendChild(typeGroup);
    entry.appendChild(paramsContainer);

    list.appendChild(entry);

    renderCompareStrategyParams(entry);
    updateButtonStates();

}


function removeStrategyEntry(entry) {

    const list = document.getElementById("compare-strategy-list");

    if (list.children.length <= MIN_STRATEGIES) {
        return;
    }

    entry.remove();
    renumberStrategyEntries();
    updateButtonStates();

}


function renumberStrategyEntries() {

    const entries = document.querySelectorAll(".compare-strategy-entry");

    entries.forEach(function(entry, i) {
        entry.dataset.index = i;
        entry.querySelector(".compare-strategy-label").textContent =
            "Strategy " + (i + 1);
    });

}


function updateButtonStates() {

    const count = document.querySelectorAll(".compare-strategy-entry").length;

    const addBtn = document.getElementById("add-strategy-btn");
    addBtn.disabled = count >= MAX_STRATEGIES;

    const removeBtns = document.querySelectorAll(".compare-remove-btn");
    removeBtns.forEach(function(btn) {
        btn.disabled = count <= MIN_STRATEGIES;
    });

}


function renderCompareStrategyParams(entry) {

    const typeSelect = entry.querySelector(".compare-strategy-type");
    const paramsContainer = entry.querySelector(".compare-strategy-params");
    const strategyType = typeSelect.value;
    const strategy = STRATEGY_REGISTRY[strategyType];

    paramsContainer.innerHTML = "";

    if (!strategy) {
        return;
    }

    for (const param of strategy.parameters) {

        const group = document.createElement("div");
        group.className = "form-group";

        const label = document.createElement("label");
        label.textContent = param.label;

        const input = document.createElement("input");
        input.type = param.type;
        input.className = "form-input compare-param-input";
        input.dataset.paramKey = param.key;
        input.value = param.default;

        if (param.min !== undefined) {
            input.min = param.min;
        }

        group.appendChild(label);
        group.appendChild(input);
        paramsContainer.appendChild(group);

    }

}


// ── Data Collection ──────────────────────────────────────────


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


function collectStrategyConfigs() {

    const entries = document.querySelectorAll(".compare-strategy-entry");
    const configs = [];

    entries.forEach(function(entry) {

        const typeSelect = entry.querySelector(".compare-strategy-type");
        const paramInputs = entry.querySelectorAll(".compare-param-input");
        const parameters = {};

        paramInputs.forEach(function(input) {
            parameters[input.dataset.paramKey] = Number(input.value);
        });

        configs.push({
            type: typeSelect.value,
            parameters: parameters,
        });

    });

    return configs;

}


// ── Validation ───────────────────────────────────────────────


function validateComparisonRequest(request) {

    const errors = [];

    if (!request.ticker) {
        errors.push("Ticker is required.");
    }

    if (!request.start_date) {
        errors.push("Start date is required.");
    }

    if (!request.end_date) {
        errors.push("End date is required.");
    }

    if (request.start_date && request.end_date && request.start_date >= request.end_date) {
        errors.push("Start date must be before end date.");
    }

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


// ── Submission ───────────────────────────────────────────────


async function onRunComparison() {

    const request = collectComparisonRequest();

    const errors = validateComparisonRequest(request);
    if (errors.length > 0) {
        showErrorModal("Validation Error", errors.join("\n"));
        return;
    }

    saveCompareConfiguration(request);

    showLoadingOverlay();

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

        renderComparisonResults(result.data);

    } catch (err) {
        showErrorModal("Network Error", err.message);
    } finally {
        hideLoadingOverlay();
    }

}


// ── Persistence ──────────────────────────────────────────────


function restoreCompareConfiguration() {

    const saved = loadCompareConfiguration();

    if (!saved) {
        addStrategyEntry();
        addStrategyEntry();
        return;
    }

    document.getElementById("compare-ticker").value = saved.ticker || "";
    document.getElementById("compare-start-date").value = saved.start_date || "";
    document.getElementById("compare-end-date").value = saved.end_date || "";
    document.getElementById("compare-capital").value = saved.initial_capital || 100000;

    const strategies = saved.strategies || [];

    if (strategies.length < MIN_STRATEGIES) {
        addStrategyEntry();
        addStrategyEntry();
        return;
    }

    strategies.forEach(function(stratConfig) {

        addStrategyEntry();

        const list = document.getElementById("compare-strategy-list");
        const entry = list.lastElementChild;

        const typeSelect = entry.querySelector(".compare-strategy-type");
        typeSelect.value = stratConfig.type;
        renderCompareStrategyParams(entry);

        if (stratConfig.parameters) {
            const inputs = entry.querySelectorAll(".compare-param-input");
            inputs.forEach(function(input) {
                var key = input.dataset.paramKey;
                if (stratConfig.parameters[key] !== undefined) {
                    input.value = stratConfig.parameters[key];
                }
            });
        }

    });

}


// ── Constants ────────────────────────────────────────────────


const STRATEGY_COLORS = [
    "#2196F3",  // Blue
    "#FF9800",  // Orange
    "#4CAF50",  // Green
    "#F44336",  // Red
    "#9C27B0",  // Purple
    "#009688",  // Teal
];

const COMPARE_METRICS = [
    { label: "CAGR", source: "portfolio_metrics", field: "cagr", format: "percentage", higherIsBetter: true },
    { label: "Total Return", source: "portfolio_metrics", field: "total_return", format: "percentage", higherIsBetter: true },
    { label: "Sharpe Ratio", source: "risk_metrics", field: "sharpe_ratio", format: "number", higherIsBetter: true },
    { label: "Sortino Ratio", source: "risk_metrics", field: "sortino_ratio", format: "number", higherIsBetter: true },
    { label: "Max Drawdown", source: "risk_metrics", field: "maximum_drawdown", format: "percentage", higherIsBetter: false },
    { label: "Win Rate", source: "trade_metrics", field: "win_rate", format: "percentage", higherIsBetter: true },
    { label: "Profit Factor", source: "trade_metrics", field: "profit_factor", format: "number", higherIsBetter: true },
    { label: "Total Trades", source: "trade_metrics", field: "total_trades", format: "integer", higherIsBetter: null },
];


// ── Helpers ──────────────────────────────────────────────────


function getStrategyLabel(strategy) {

    const reg = STRATEGY_REGISTRY[strategy.type];
    const label = reg ? reg.label : strategy.type;
    const paramValues = Object.values(strategy.parameters).join("/");
    return label + " (" + paramValues + ")";

}


// ── Main Renderer ────────────────────────────────────────────


function renderComparisonResults(data) {

    renderCompareSummary(data.common, data.results);
    renderCompareMatrix(data.results);
    renderCompareEquityChart(data.results, data.benchmark);
    renderCompareDrawdownChart(data.results);
    renderCompareTradeHistory(data.results);

}


// ── 1. Summary Header ───────────────────────────────────────


function renderCompareSummary(common, results) {

    const section = document.getElementById("compare-summary-section");
    section.innerHTML = "";

    const total = results.length;
    const successful = results.filter(function(r) { return r.success; }).length;
    const failed = total - successful;

    const div = document.createElement("div");
    div.className = "compare-summary";

    div.innerHTML =
        '<span><strong>' + common.ticker + '</strong></span>' +
        '<span>' + common.start_date + ' \u2192 ' + common.end_date + '</span>' +
        '<span>Capital: ' + formatCurrency(common.initial_capital) + '</span>' +
        '<span>' + total + ' strategies: ' + successful + ' successful, ' + failed + ' failed</span>';

    section.appendChild(div);

}


// ── 2. Metrics Matrix ───────────────────────────────────────


function renderCompareMatrix(results) {

    const container = document.getElementById("compare-matrix-container");
    container.innerHTML = "";

    const table = document.createElement("table");
    table.className = "compare-matrix-table";

    // Header row
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    const emptyTh = document.createElement("th");
    headerRow.appendChild(emptyTh);

    results.forEach(function(result) {
        const th = document.createElement("th");
        th.textContent = getStrategyLabel(result.strategy);
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Body rows
    const tbody = document.createElement("tbody");

    COMPARE_METRICS.forEach(function(metric) {

        const row = document.createElement("tr");

        const labelCell = document.createElement("td");
        labelCell.className = "compare-matrix-label";
        labelCell.textContent = metric.label;
        row.appendChild(labelCell);

        const values = [];
        const cells = [];

        results.forEach(function(result) {

            const cell = document.createElement("td");

            if (!result.success || !result[metric.source]) {
                cell.textContent = "Error";
                cell.className = "compare-matrix-error";
                values.push(null);
            } else {
                const val = result[metric.source][metric.field];
                cell.textContent = formatByType(val, metric.format);
                values.push(val);
            }

            cells.push(cell);
            row.appendChild(cell);

        });

        // Highlight best value (skip neutral metrics where higherIsBetter is null)
        if (metric.higherIsBetter !== null) {

            const validValues = values.filter(function(v) { return v !== null && v !== undefined; });

            if (validValues.length > 0) {

                var bestVal;

                if (metric.higherIsBetter) {
                    bestVal = Math.max.apply(null, validValues);
                } else {
                    bestVal = validValues.reduce(function(a, b) {
                        return Math.abs(a) < Math.abs(b) ? a : b;
                    });
                }

                values.forEach(function(v, i) {
                    if (v === bestVal && cells[i]) {
                        cells[i].classList.add("compare-best");
                    }
                });

            }

        }

        tbody.appendChild(row);

    });

    table.appendChild(tbody);
    container.appendChild(table);

}


// ── 3. Equity Curve Overlay ─────────────────────────────────


function renderCompareEquityChart(results, benchmark) {

    const traces = [];
    let colorIndex = 0;

    results.forEach(function(result) {

        if (!result.success || !result.analytics_history) {
            return;
        }

        traces.push({
            x: result.analytics_history.map(function(r) { return r.Date; }),
            y: result.analytics_history.map(function(r) { return r["Portfolio Value"]; }),
            mode: "lines",
            name: getStrategyLabel(result.strategy),
            line: { color: STRATEGY_COLORS[colorIndex % STRATEGY_COLORS.length] },
        });

        colorIndex++;

    });

    if (benchmark && benchmark.portfolio_history) {

        traces.push({
            x: benchmark.portfolio_history.map(function(r) { return r.Date; }),
            y: benchmark.portfolio_history.map(function(r) { return r["Buy & Hold Value"]; }),
            mode: "lines",
            name: "Buy & Hold",
            line: { color: "#9E9E9E", dash: "dot" },
        });

    }

    const layout = {
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        margin: { l: 60, r: 20, t: 40, b: 50 },
        xaxis: { title: "Date", gridcolor: "#3b4659", zeroline: false, nticks: 12 },
        yaxis: { title: "Portfolio Value", gridcolor: "#3b4659", zeroline: false },
        font: { color: "#FFFFFF" },
        legend: { orientation: "h", x: 0, y: 1.05 },
        dragmode: "pan",
    };

    Plotly.newPlot(
        document.getElementById("compare-equity-chart"),
        traces,
        layout,
        { responsive: true, displayModeBar: false, scrollZoom: true }
    );

}


// ── 4. Drawdown Comparison ──────────────────────────────────


function renderCompareDrawdownChart(results) {

    const traces = [];
    let colorIndex = 0;

    results.forEach(function(result) {

        if (!result.success || !result.analytics_history) {
            return;
        }

        traces.push({
            x: result.analytics_history.map(function(r) { return r.Date; }),
            y: result.analytics_history.map(function(r) { return r.Drawdown; }),
            mode: "lines",
            fill: "tozeroy",
            name: getStrategyLabel(result.strategy),
            line: { color: STRATEGY_COLORS[colorIndex % STRATEGY_COLORS.length] },
        });

        colorIndex++;

    });

    const layout = {
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        margin: { l: 60, r: 20, t: 40, b: 50 },
        xaxis: { title: "Date", gridcolor: "#3b4659", zeroline: false, nticks: 12 },
        yaxis: { title: "Drawdown (%)", gridcolor: "#3b4659", zeroline: true, rangemode: "tozero" },
        font: { color: "#FFFFFF" },
        legend: { orientation: "h", x: 0, y: 1.05 },
        dragmode: "pan",
    };

    Plotly.newPlot(
        document.getElementById("compare-drawdown-chart"),
        traces,
        layout,
        { responsive: true, displayModeBar: false, scrollZoom: true }
    );

}


// ── 5. Trade History (Tabbed) ───────────────────────────────


function renderCompareTradeHistory(results) {

    const tabsContainer = document.getElementById("compare-trades-tabs");
    const contentContainer = document.getElementById("compare-trades-content");

    tabsContainer.innerHTML = "";
    contentContainer.innerHTML = "";

    results.forEach(function(result, i) {

        const label = getStrategyLabel(result.strategy);

        // Tab button
        const btn = document.createElement("button");
        btn.className = "compare-trade-tab" + (i === 0 ? " active" : "");
        btn.dataset.index = i;
        btn.textContent = label;

        btn.addEventListener("click", function() {

            tabsContainer.querySelectorAll(".compare-trade-tab").forEach(function(b) {
                b.classList.remove("active");
            });
            btn.classList.add("active");

            contentContainer.querySelectorAll(".compare-trade-panel").forEach(function(p) {
                p.classList.remove("active");
            });
            document.getElementById("compare-trade-panel-" + i).classList.add("active");

        });

        tabsContainer.appendChild(btn);

        // Content panel
        const panel = document.createElement("div");
        panel.className = "compare-trade-panel" + (i === 0 ? " active" : "");
        panel.id = "compare-trade-panel-" + i;

        if (!result.success) {

            panel.innerHTML = '<p class="compare-trade-error">' +
                'Strategy failed: ' + (result.error || "Unknown error") + '</p>';

        } else if (!result.trade_history || result.trade_history.length === 0) {

            panel.innerHTML = '<p class="compare-trade-empty">No trades executed.</p>';

        } else {

            const table = document.createElement("table");
            table.className = "compare-trade-table";

            table.innerHTML =
                '<thead><tr>' +
                '<th>Entry Date</th>' +
                '<th>Exit Date</th>' +
                '<th>Holding Period</th>' +
                '<th>Entry Price</th>' +
                '<th>Exit Price</th>' +
                '<th>Quantity</th>' +
                '<th>Investment</th>' +
                '<th>Exit Value</th>' +
                '<th>Return %</th>' +
                '<th>Profit / Loss</th>' +
                '</tr></thead>';

            const tbody = document.createElement("tbody");

            result.trade_history.forEach(function(trade) {

                const row = document.createElement("tr");
                row.innerHTML =
                    '<td>' + formatDate(trade.entry_date) + '</td>' +
                    '<td>' + formatDate(trade.exit_date) + '</td>' +
                    '<td>' + trade.holding_period + ' Days</td>' +
                    '<td>' + formatCurrency(trade.entry_price) + '</td>' +
                    '<td>' + formatCurrency(trade.exit_price) + '</td>' +
                    '<td>' + trade.shares + '</td>' +
                    '<td>' + formatCurrency(trade.investment) + '</td>' +
                    '<td>' + formatCurrency(trade.exit_value) + '</td>' +
                    '<td>' + formatPercentage(trade.return_pct) + '</td>' +
                    '<td>' + formatCurrency(trade.profit_loss) + '</td>';
                tbody.appendChild(row);

            });

            table.appendChild(tbody);
            panel.appendChild(table);

        }

        contentContainer.appendChild(panel);

    });

}
