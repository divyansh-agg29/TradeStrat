"use strict";

const ui = {

    tickerInput:
        document.getElementById("ticker"),

    startDateInput:
        document.getElementById("start-date"),

    endDateInput:
        document.getElementById("end-date"),

    capitalInput:
        document.getElementById("capital"),

    strategySelect:
        document.getElementById("strategy-type"),

    strategyParametersContainer:
        document.getElementById("strategy-parameters"),

    runButton:
        document.getElementById("run-backtest-btn"),

    // KPI Cards

    totalReturnCard:
        document.getElementById("kpi-total-return"),

    cagrCard:
        document.getElementById("kpi-cagr"),

    sharpeRatioCard:
        document.getElementById("kpi-sharpe-ratio"),

    maxDrawdownCard:
        document.getElementById("kpi-max-drawdown"),

    finalPortfolioCard:
        document.getElementById("kpi-final-portfolio-value"),

    winRateCard:
        document.getElementById("kpi-win-rate"),

    profitFactorCard:
        document.getElementById("kpi-profit-factor"),

    totalTradesCard:
        document.getElementById("kpi-total-trades"),
    

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

    const configuration =
        readConfigurationForm();

    const validation =
        validateConfiguration(configuration);

    if (!validation.isValid) {
        console.log(validation.errors);
        return;
    }

    saveConfiguration(configuration);

    const response = await runBacktest(configuration);
    console.log("Backtest Response:", response);

    renderDashboard(response);


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

    return {

        ticker: ui.tickerInput.value.trim(),

        startDate: ui.startDateInput.value,

        endDate: ui.endDateInput.value,

        initialCapital: Number(
            ui.capitalInput.value
        ),

        strategy: {

            type: strategyType,

            parameters: parameters

        }

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
