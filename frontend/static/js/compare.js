"use strict";

// Compare tab logic

const MIN_STRATEGIES = 2;
const MAX_STRATEGIES = 6;


// ── Initialization ───────────────────────────────────────────


function initCompareForm() {

    addStrategyEntry();
    addStrategyEntry();

    document.getElementById("add-strategy-btn")
        .addEventListener("click", addStrategyEntry);

    document.getElementById("run-comparison-btn")
        .addEventListener("click", onRunComparison);

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

        // Phase 7: renderComparisonResults(result.data);
        console.log("Comparison result:", result.data);

    } catch (err) {
        showErrorModal("Network Error", err.message);
    } finally {
        hideLoadingOverlay();
    }

}
