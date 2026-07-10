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

    shortPeriodInput:
        document.getElementById("short-period"),

    longPeriodInput:
        document.getElementById("long-period"),

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

    return {

        ticker: ui.tickerInput.value.trim(),

        startDate: ui.startDateInput.value,

        endDate: ui.endDateInput.value,

        initialCapital: Number(
            ui.capitalInput.value
        ),

        strategy: {

            type:
                ui.strategySelect.value,

            shortPeriod: Number(
                ui.shortPeriodInput.value
            ),

            longPeriod: Number(
                ui.longPeriodInput.value
            )

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

    if (
        configuration.strategy.shortPeriod <= 0
    ) {

        errors.push(
            "Short SMA period must be positive."
        );

    }

    if (
        configuration.strategy.longPeriod <= 0
    ) {

        errors.push(
            "Long SMA period must be positive."
        );

    }

    if (
        configuration.strategy.shortPeriod >=
        configuration.strategy.longPeriod
    ) {

        errors.push(
            "Short SMA period must be smaller than Long SMA period."
        );

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

    ui.shortPeriodInput.value =
        configuration.strategy.shortPeriod;

    ui.longPeriodInput.value =
        configuration.strategy.longPeriod;

}
