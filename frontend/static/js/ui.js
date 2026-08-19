"use strict";

const ui = {

    // Base Configuration

    tickerInput:
        document.getElementById("ticker"),

    startDateInput:
        document.getElementById("start-date"),

    endDateInput:
        document.getElementById("end-date"),

    capitalInput:
        document.getElementById("capital"),

    intervalSelect:
        document.getElementById("interval"),

    // Strategy Configuration

    strategySelect:
        document.getElementById("strategy-type"),

    strategyParametersContainer:
        document.getElementById("strategy-parameters"),
    
    // Stop Loss Configuration

    stopLossEnabledCheckbox:
        document.getElementById("stop-loss-enabled"),

    stopLossTypeSelect:
        document.getElementById("stop-loss-type"),

    stopLossParametersContainer:
        document.getElementById("stop-loss-parameters"),
    
    // Take Profit Configuration

    takeProfitEnabledCheckbox:
        document.getElementById("take-profit-enabled"),

    takeProfitTypeSelect:
        document.getElementById("take-profit-type"),

    takeProfitParametersContainer:
        document.getElementById("take-profit-parameters"),
    
    // Position Sizing Configuration

    positionSizingEnabledCheckbox:
        document.getElementById("position-sizing-enabled"),

    positionSizingTypeSelect:
        document.getElementById("position-sizing-type"),

    positionSizingParametersContainer:
        document.getElementById("position-sizing-parameters"),

    // Run Button

    runButton:
        document.getElementById("run-backtest-btn"),

    // Portfolio Metrics

    portfolioInitialCapital:
        document.getElementById("metric-initial-capital"),
    
    portfolioFinalValue:
        document.getElementById("metric-final-portfolio-value"),
    
    portfolioProfitLossPercent:
        document.getElementById("metric-profit-loss-percent"),

    portfolioTotalReturn:
        document.getElementById("metric-total-return"),
    
    portfolioCagr:
        document.getElementById("metric-cagr"),
    

    // Risk Metrics

    riskVolatility:
        document.getElementById("metric-volatility"),
    
    riskSharpeRatio:
        document.getElementById("metric-sharpe-ratio"),
    
    riskMaximumDrawdown:
        document.getElementById("metric-maximum-drawdown"),

    riskSortinoRatio:
        document.getElementById("metric-sortino-ratio"),

    riskCalmarRatio:
        document.getElementById("metric-calmar-ratio"),
    

    // Benchmark Metrics

    benchmarkFinalValue:
        document.getElementById("metric-benchmark-final-value"),

    benchmarkReturn:
        document.getElementById("metric-benchmark-return"),

    benchmarkAlpha:
        document.getElementById("metric-alpha"),


    // Trade Metrics

    tradeTotalTrades:
        document.getElementById("metric-total-trades"),
    
    tradeWinningTrades:
        document.getElementById("metric-winning-trades"),
    
    tradeLosingTrades:
        document.getElementById("metric-losing-trades"),
    
    tradeWinRate:
        document.getElementById("metric-win-rate"),
    
    tradeProfitFactor:
        document.getElementById("metric-profit-factor"),
    
    tradeAverageWinner:
        document.getElementById("metric-average-winner"),
    
    tradeAverageLoser:
        document.getElementById("metric-average-loser"),
    
    tradeLargestWinner:
        document.getElementById("metric-largest-winner"),
    
    tradeLargestLoser:
        document.getElementById("metric-largest-loser"),
    
    tradeAverageHoldingPeriod:
        document.getElementById("metric-average-holding-period"),
    

    // Trade History Table
    tradeHistoryBody:
        document.getElementById("trade-history-body"),
    
    // Charts    
    priceChart:
        document.getElementById("price-chart"),
    
    equityChart: 
        document.getElementById("equity-chart"),
    
    drawdownChart: 
        document.getElementById("drawdown-chart"),

};

function registerEventListeners() {

    ui.runButton.addEventListener(
        "click",
        onRunBacktestClicked
    );

    ui.strategySelect.addEventListener(
        "change",
        onStrategyChanged
    );

    ui.stopLossEnabledCheckbox.addEventListener(
        "change",
        onStopLossCheckboxChanged
    );

    ui.stopLossTypeSelect.addEventListener(
        "change",
        onStopLossTypeChanged
    );

    ui.takeProfitEnabledCheckbox.addEventListener(
        "change",
        onTakeProfitCheckboxChanged
    );

    ui.takeProfitTypeSelect.addEventListener(
        "change",
        onTakeProfitTypeChanged
    );

    ui.positionSizingEnabledCheckbox.addEventListener(
        "change",
        onPositionSizingCheckboxChanged
    );

    ui.positionSizingTypeSelect.addEventListener(
        "change",
        onPositionSizingTypeChanged
    );

}

function onStopLossCheckboxChanged() {

    const isEnabled = ui.stopLossEnabledCheckbox.checked;

    const fieldContainer = document.getElementById("stop-loss-field-container");
    fieldContainer.style.display = isEnabled ? "block" : "none";

    if (!isEnabled) {
        ui.stopLossParametersContainer.innerHTML = "";
    } else {
        onStopLossTypeChanged();
    }

}


function onTakeProfitCheckboxChanged() {

    const isEnabled = ui.takeProfitEnabledCheckbox.checked;

    const fieldContainer = document.getElementById("take-profit-field-container");
    fieldContainer.style.display = isEnabled ? "block" : "none";

    if (!isEnabled) {
        ui.takeProfitParametersContainer.innerHTML = "";
    } else {
        onTakeProfitTypeChanged();
    }

}


function populateTakeProfitDropdown() {

    ui.takeProfitTypeSelect.innerHTML = "";

    for (const [key, rule] of Object.entries(TAKE_PROFIT_REGISTRY)) {

        const option = document.createElement("option");
        option.value = key;
        option.textContent = rule.label;
        ui.takeProfitTypeSelect.appendChild(option);

    }

}


function onTakeProfitTypeChanged() {

    const takeProfitType = ui.takeProfitTypeSelect.value;
    const rule = TAKE_PROFIT_REGISTRY[takeProfitType];

    ui.takeProfitParametersContainer.innerHTML = "";

    if (!rule) {
        return;
    }

    for (const param of rule.parameters) {

        const group = document.createElement("div");
        group.className = "form-group";

        const label = document.createElement("label");
        label.setAttribute("for", "tp-param-" + param.key);
        label.textContent = param.label;

        const input = document.createElement("input");
        input.type = param.type;
        input.id = "tp-param-" + param.key;
        input.className = "form-input";
        input.value = param.default;

        if (param.min !== undefined) {
            input.min = param.min;
        }

        if (param.step !== undefined) {
            input.step = param.step;
        }

        group.appendChild(label);
        group.appendChild(input);
        ui.takeProfitParametersContainer.appendChild(group);

    }

}


function onPositionSizingCheckboxChanged() {

    const isEnabled = ui.positionSizingEnabledCheckbox.checked;

    const fieldContainer = document.getElementById("position-sizing-field-container");
    fieldContainer.style.display = isEnabled ? "block" : "none";

    if (!isEnabled) {
        ui.positionSizingParametersContainer.innerHTML = "";
    } else {
        onPositionSizingTypeChanged();
    }

}


function populatePositionSizingDropdown() {

    ui.positionSizingTypeSelect.innerHTML = "";

    for (const [key, rule] of Object.entries(POSITION_SIZING_REGISTRY)) {

        const option = document.createElement("option");
        option.value = key;
        option.textContent = rule.label;
        ui.positionSizingTypeSelect.appendChild(option);

    }

}


function onPositionSizingTypeChanged() {

    const sizingType = ui.positionSizingTypeSelect.value;
    const rule = POSITION_SIZING_REGISTRY[sizingType];

    ui.positionSizingParametersContainer.innerHTML = "";

    if (!rule) {
        return;
    }

    for (const param of rule.parameters) {

        const group = document.createElement("div");
        group.className = "form-group";

        const label = document.createElement("label");
        label.setAttribute("for", "sizing-param-" + param.key);
        label.textContent = param.label;

        const input = document.createElement("input");
        input.type = param.type;
        input.id = "sizing-param-" + param.key;
        input.className = "form-input";
        input.value = param.default;

        if (param.min !== undefined) {
            input.min = param.min;
        }

        if (param.step !== undefined) {
            input.step = param.step;
        }

        group.appendChild(label);
        group.appendChild(input);
        ui.positionSizingParametersContainer.appendChild(group);

    }

}


function populateStopLossDropdown() {

    ui.stopLossTypeSelect.innerHTML = "";

    for (const [key, rule] of Object.entries(STOP_LOSS_REGISTRY)) {

        const option = document.createElement("option");
        option.value = key;
        option.textContent = rule.label;
        ui.stopLossTypeSelect.appendChild(option);

    }

}


function onStopLossTypeChanged() {

    const stopLossType = ui.stopLossTypeSelect.value;
    const rule = STOP_LOSS_REGISTRY[stopLossType];

    ui.stopLossParametersContainer.innerHTML = "";

    if (!rule) {
        return;
    }

    for (const param of rule.parameters) {

        const group = document.createElement("div");
        group.className = "form-group";

        const label = document.createElement("label");
        label.setAttribute("for", "risk-param-" + param.key);
        label.textContent = param.label;

        const input = document.createElement("input");
        input.type = param.type;
        input.id = "risk-param-" + param.key;
        input.className = "form-input";
        input.value = param.default;

        if (param.min !== undefined) {
            input.min = param.min;
        }

        if (param.step !== undefined) {
            input.step = param.step;
        }

        group.appendChild(label);
        group.appendChild(input);
        ui.stopLossParametersContainer.appendChild(group);

    }

}


function populateStrategyDropdown() {

    ui.strategySelect.innerHTML = "";

    for (const [key, strategy] of Object.entries(STRATEGY_REGISTRY)) {

        const option = document.createElement("option");
        option.value = key;
        option.textContent = strategy.label;
        ui.strategySelect.appendChild(option);

    }

}

function onStrategyChanged() {

    const strategyType = ui.strategySelect.value;
    const strategy = STRATEGY_REGISTRY[strategyType];

    ui.strategyParametersContainer.innerHTML = "";

    if (!strategy) {
        return;
    }

    for (const param of strategy.parameters) {

        const group = document.createElement("div");
        group.className = "form-group";

        const label = document.createElement("label");
        label.setAttribute("for", "param-" + param.key);
        label.textContent = param.label;

        const input = document.createElement("input");
        input.type = param.type;
        input.id = "param-" + param.key;
        input.className = "form-input";
        input.value = param.default;

        if (param.min !== undefined) {
            input.min = param.min;
        }

        group.appendChild(label);
        group.appendChild(input);
        ui.strategyParametersContainer.appendChild(group);

    }

}

async function onRunBacktestClicked() {

    showLoadingOverlay();

    try{
        const configuration =
            readConfigurationForm();
        const validation =
            validateConfiguration(configuration);

        if (!validation.isValid) {
            showErrorModal(
                "Invalid Configuration",
                validation.errors.join("\n")
            );
            return;
        }

        saveConfiguration(configuration);

        const response = await runBacktest(configuration);
        console.log("Backtest Response:", response);

        renderDashboard(response);
    }
    catch (error) {

        console.error(error);

        showErrorModal(
            "Backtest Failed",
            error.message
        );

    }
    finally {
        hideLoadingOverlay();
    };

    

}

function readConfigurationForm() {

    const strategyType = ui.strategySelect.value;
    const strategy = STRATEGY_REGISTRY[strategyType];
    const parameters = {};

    if (strategy) {

        for (const param of strategy.parameters) {

            const input = document.getElementById(
                "param-" + param.key
            );

            if (input) {
                parameters[param.key] = Number(input.value);
            }

        }

    }

    const stopLossEnabled = ui.stopLossEnabledCheckbox.checked;
    const risk = {};

    if (stopLossEnabled) {
        const stopLossType = ui.stopLossTypeSelect.value;
        const rule = STOP_LOSS_REGISTRY[stopLossType];

        if (rule) {
            const rawParams = {};

            for (const param of rule.parameters) {
                const input = document.getElementById("risk-param-" + param.key);
                if (input) {
                    rawParams[param.key] = Number(input.value);
                }
            }

            risk.stopLossType = stopLossType;
            risk.parameters = rule.toPayload(rawParams);
        }
    }

    const takeProfitEnabled = ui.takeProfitEnabledCheckbox.checked;

    if (takeProfitEnabled) {
        const takeProfitType = ui.takeProfitTypeSelect.value;
        const tpRule = TAKE_PROFIT_REGISTRY[takeProfitType];

        if (tpRule) {
            const rawTpParams = {};

            for (const param of tpRule.parameters) {
                const input = document.getElementById("tp-param-" + param.key);
                if (input) {
                    rawTpParams[param.key] = Number(input.value);
                }
            }

            risk.takeProfitType = takeProfitType;
            risk.takeProfitParameters = tpRule.toPayload(rawTpParams);
        }
    }

    const positionSizingEnabled = ui.positionSizingEnabledCheckbox.checked;
    const positionSizing = {};

    if (positionSizingEnabled) {
        const sizingType = ui.positionSizingTypeSelect.value;
        const sizingRule = POSITION_SIZING_REGISTRY[sizingType];

        if (sizingRule) {
            const rawSizingParams = {};

            for (const param of sizingRule.parameters) {
                const input = document.getElementById("sizing-param-" + param.key);
                if (input) {
                    rawSizingParams[param.key] = Number(input.value);
                }
            }

            positionSizing.sizingType = sizingType;
            positionSizing.parameters = sizingRule.toPayload(rawSizingParams);
        }
    }

    return {

        ticker: ui.tickerInput.value.trim(),

        startDate: ui.startDateInput.value,

        endDate: ui.endDateInput.value,

        initialCapital: Number(
            ui.capitalInput.value
        ),

        interval: ui.intervalSelect.value,

        strategy: {

            type: strategyType,

            parameters: parameters

        },

        risk: risk,

        positionSizing: positionSizing

    };

}

function validateConfiguration(configuration) {

    const errors = [];

    if (configuration.ticker.length === 0) {

        errors.push(
            "Ticker is required."
        );

    }

    if (configuration.initialCapital <= 0) {

        errors.push(
            "Initial capital must be greater than zero."
        );

    }

    if (
        configuration.startDate &&
        configuration.endDate &&
        configuration.startDate > configuration.endDate
    ) {

        errors.push(
            "Start date must be before end date."
        );

    }

    // Validate interval and date range compatibility
    if (configuration.interval && configuration.startDate && configuration.endDate) {
        const intervalValidation = validateIntervalDateRange(
            configuration.interval,
            configuration.startDate,
            configuration.endDate
        );

        if (!intervalValidation.valid) {
            errors.push(intervalValidation.error);
        }
    }

    if (configuration.risk && configuration.risk.stopLossType) {
        const rule = STOP_LOSS_REGISTRY[configuration.risk.stopLossType];
        if (rule && rule.validate) {
            const riskErrors = rule.validate(configuration.risk.parameters || {});
            errors.push(...riskErrors);
        }
    }

    if (configuration.risk && configuration.risk.takeProfitType) {
        const tpRule = TAKE_PROFIT_REGISTRY[configuration.risk.takeProfitType];
        if (tpRule && tpRule.validate) {
            const tpErrors = tpRule.validate(configuration.risk.takeProfitParameters || {});
            errors.push(...tpErrors);
        }
    }

    if (configuration.positionSizing && configuration.positionSizing.sizingType) {
        const sizingRule = POSITION_SIZING_REGISTRY[configuration.positionSizing.sizingType];
        if (sizingRule && sizingRule.validate) {
            const sizingErrors = sizingRule.validate(configuration.positionSizing.parameters || {});
            errors.push(...sizingErrors);
        }
    }

    const strategy =
        STRATEGY_REGISTRY[configuration.strategy.type];

    if (strategy && strategy.validate) {

        const strategyErrors = strategy.validate(
            configuration.strategy.parameters
        );

        errors.push(...strategyErrors);

    }

    return {

        isValid: errors.length === 0,

        errors: errors

    };

}

function populateConfigurationForm(configuration) {

    ui.tickerInput.value =
        configuration.ticker;

    ui.startDateInput.value =
        configuration.startDate;

    ui.endDateInput.value =
        configuration.endDate;

    ui.capitalInput.value =
        configuration.initialCapital;

    if (configuration.interval) {
        ui.intervalSelect.value = configuration.interval;
        // Update the interval hint to match the restored value
        updateIntervalHint(configuration.interval, "interval-hint");
    }

    if (configuration.risk && configuration.risk.stopLossType) {
        ui.stopLossEnabledCheckbox.checked = true;
        document.getElementById("stop-loss-field-container").style.display = "block";

        ui.stopLossTypeSelect.value = configuration.risk.stopLossType;
        onStopLossTypeChanged();

        const rule = STOP_LOSS_REGISTRY[configuration.risk.stopLossType];
        if (rule && configuration.risk.parameters) {
            const displayParams = rule.fromPayload(configuration.risk.parameters);
            for (const [key, value] of Object.entries(displayParams)) {
                const input = document.getElementById("risk-param-" + key);
                if (input) {
                    input.value = value;
                }
            }
        }
    } else {
        ui.stopLossEnabledCheckbox.checked = false;
        document.getElementById("stop-loss-field-container").style.display = "none";
    }

    if (configuration.risk && configuration.risk.takeProfitType) {
        ui.takeProfitEnabledCheckbox.checked = true;
        document.getElementById("take-profit-field-container").style.display = "block";

        ui.takeProfitTypeSelect.value = configuration.risk.takeProfitType;
        onTakeProfitTypeChanged();

        const tpRule = TAKE_PROFIT_REGISTRY[configuration.risk.takeProfitType];
        if (tpRule && configuration.risk.takeProfitParameters) {
            const displayParams = tpRule.fromPayload(configuration.risk.takeProfitParameters);
            for (const [key, value] of Object.entries(displayParams)) {
                const input = document.getElementById("tp-param-" + key);
                if (input) {
                    input.value = value;
                }
            }
        }
    } else {
        ui.takeProfitEnabledCheckbox.checked = false;
        document.getElementById("take-profit-field-container").style.display = "none";
    }

    if (configuration.positionSizing && configuration.positionSizing.sizingType) {
        ui.positionSizingEnabledCheckbox.checked = true;
        document.getElementById("position-sizing-field-container").style.display = "block";

        ui.positionSizingTypeSelect.value = configuration.positionSizing.sizingType;
        onPositionSizingTypeChanged();

        const sizingRule = POSITION_SIZING_REGISTRY[configuration.positionSizing.sizingType];
        if (sizingRule && configuration.positionSizing.parameters) {
            const displayParams = sizingRule.fromPayload(configuration.positionSizing.parameters);
            for (const [key, value] of Object.entries(displayParams)) {
                const input = document.getElementById("sizing-param-" + key);
                if (input) {
                    input.value = value;
                }
            }
        }
    } else {
        ui.positionSizingEnabledCheckbox.checked = false;
        document.getElementById("position-sizing-field-container").style.display = "none";
    }

    ui.strategySelect.value =
        configuration.strategy.type;

    onStrategyChanged();

    // Support both new format (parameters object) and legacy format (shortPeriod/longPeriod)
    let params = configuration.strategy.parameters;

    if (!params && configuration.strategy.shortPeriod !== undefined) {
        params = {
            short_period: configuration.strategy.shortPeriod,
            long_period: configuration.strategy.longPeriod
        };
    }

    if (params) {

        for (const [key, value] of Object.entries(params)) {

            const input = document.getElementById(
                "param-" + key
            );

            if (input) {
                input.value = value;
            }

        }

    }

}
