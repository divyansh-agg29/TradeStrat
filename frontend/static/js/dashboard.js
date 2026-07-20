"use strict";

function renderDashboard(response) {

    const data = response.data;

    renderKPICards(data.portfolio_metrics, data.risk_metrics, data.trade_metrics);

    renderPortfolioMetrics(data.portfolio_metrics);

    renderRiskMetrics(data.risk_metrics);

    renderBenchmarkMetrics(data.benchmark_metrics);

    renderTradeStatistics(data.trade_metrics);

    renderCharts(data);

    renderTradeHistory(data.trade_history);

}

function renderKPICards(portfolioMetrics, riskMetrics, tradeMetrics) {

    ui.totalReturnCard.textContent =
        formatPercentage(
            portfolioMetrics.total_return
        );

    ui.cagrCard.textContent =
        formatPercentage(
            portfolioMetrics.cagr
        );

    ui.sharpeRatioCard.textContent =
        formatNumber(
            riskMetrics.sharpe_ratio
        );

    ui.maxDrawdownCard.textContent =
        formatPercentage(
            riskMetrics.maximum_drawdown
        );

    ui.finalPortfolioCard.textContent =
        formatCurrency(
            portfolioMetrics.final_portfolio_value
        );

    ui.winRateCard.textContent =
        formatPercentage(
            tradeMetrics.win_rate
        );

    ui.profitFactorCard.textContent =
        formatNumber(
            tradeMetrics.profit_factor
        );

    ui.totalTradesCard.textContent =
        tradeMetrics.total_trades;

}


function renderPortfolioMetrics(portfolioMetrics) {

    ui.portfolioInitialCapital.textContent =
        formatCurrency(portfolioMetrics.initial_capital);

    ui.portfolioFinalValue.textContent =
        formatCurrency(portfolioMetrics.final_portfolio_value);

    ui.portfolioProfitLossPercent.textContent =
        formatPercentage(portfolioMetrics.total_return);

    ui.portfolioTotalReturn.textContent =
        formatCurrency(portfolioMetrics.profit_loss);

    ui.portfolioCagr.textContent =
        formatPercentage(portfolioMetrics.cagr);

}


function renderRiskMetrics(riskMetrics) {

    ui.riskVolatility.textContent =
        formatPercentage(riskMetrics.annualized_volatility);

    ui.riskSharpeRatio.textContent =
        formatNumber(riskMetrics.sharpe_ratio);

    ui.riskMaximumDrawdown.textContent =
        formatPercentage(riskMetrics.maximum_drawdown);

    ui.riskSortinoRatio.textContent =
        formatNumber(riskMetrics.sortino_ratio);

    ui.riskCalmarRatio.textContent =
        formatNumber(riskMetrics.calmar_ratio);

}


function renderBenchmarkMetrics(benchmarkMetrics) {

    ui.benchmarkFinalValue.textContent =
        formatCurrency(benchmarkMetrics.benchmark_final_value);

    ui.benchmarkReturn.textContent =
        formatPercentage(benchmarkMetrics.benchmark_return);

    ui.benchmarkAlpha.textContent =
        formatPercentage(benchmarkMetrics.alpha);

}


function renderTradeStatistics(tradeMetrics) {

    ui.tradeTotalTrades.textContent =
        tradeMetrics.total_trades;

    ui.tradeWinningTrades.textContent =
        tradeMetrics.winning_trades;

    ui.tradeLosingTrades.textContent =
        tradeMetrics.losing_trades;

    ui.tradeWinRate.textContent =
        formatPercentage(tradeMetrics.win_rate);

    ui.tradeProfitFactor.textContent =
        formatNumber(tradeMetrics.profit_factor);

    ui.tradeAverageWinner.textContent =
        formatCurrency(tradeMetrics.average_winning_trade);

    ui.tradeAverageLoser.textContent =
        formatCurrency(tradeMetrics.average_losing_trade);

    ui.tradeLargestWinner.textContent =
        formatCurrency(tradeMetrics.largest_winner);

    ui.tradeLargestLoser.textContent =
        formatCurrency(tradeMetrics.largest_loser);

    ui.tradeAverageHoldingPeriod.textContent =
        `${formatNumber(tradeMetrics.average_holding_period)} Days`;

}


function renderCharts(data) {

    renderPriceChart(data.portfolio_history);

    renderEquityChart(data.analytics_history);

    renderDrawdownChart(data.analytics_history);

}


function renderTradeHistory(trades) {

    ui.tradeHistoryBody.innerHTML = "";

    for (const trade of trades) {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${formatDate(trade.entry_date)}</td>
            <td>${formatDate(trade.exit_date)}</td>
            <td>${trade.holding_period} Days</td>
            <td>${formatCurrency(trade.entry_price)}</td>
            <td>${formatCurrency(trade.exit_price)}</td>
            <td>${trade.shares}</td>
            <td>${formatCurrency(trade.investment)}</td>
            <td>${formatCurrency(trade.exit_value)}</td>
            <td>${formatPercentage(trade.return_pct)}</td>
            <td>${formatCurrency(trade.profit_loss)}</td>
        `;

        ui.tradeHistoryBody.appendChild(row);

    }

}


function renderPriceChart(portfolioHistory) {

    const dates =
        portfolioHistory.map(
            row => row.Date
        );

    const closePrices =
        portfolioHistory.map(
            row => row.Close
        );
    

    const traces = [];

    // Push the Close Price trace to list of traces to be plotted
    traces.push({
        x: dates,
        y: closePrices,
        mode: "lines",
        name: "Close"
    });

    // Pushing traces for each indicator column in the portfolio history to be plotted
    const columns = Object.keys(portfolioHistory[0]);
    const knownColumns = new Set([
        "Date", "Open", "High", "Low", "Close", "Volume",
        "Signal", "Cash", "Shares", "Holdings Value",
        "Portfolio Value", "Position"
    ]);
    const indicatorPrefixes = [
        "SMA",
        "EMA",
        "RSI",
        "MACD",
        "BB"
    ];

    for (const column of columns)
    {
        const isIndicator = indicatorPrefixes.some(
            prefix => column.startsWith(prefix)
        );

        if (!isIndicator)
        {
            continue;
        }

        traces.push({
            x: dates,
            y: portfolioHistory.map(
                row => row[column]
            ),
            mode: "lines",
            name: column
        });
    }

    // Pushing traces for BUY signals to be plotted
    const buySignals = portfolioHistory.filter(
        row => row.Signal === "BUY"
    );

    traces.push({

        x: buySignals.map(
            row => row.Date
        ),

        y: buySignals.map(
            row => row.Close
        ),

        mode: "markers",

        name: "BUY",

        marker: {

            symbol: "triangle-up",
            size: 8,
            color: "#00C853",
            line: {
                width: 1,
                color: "#FFFFFF"
            }
        }

    });

    // Pushing traces for SELL signals to be plotted
    const sellSignals = portfolioHistory.filter(
        row => row.Signal === "SELL"
    );

    traces.push({

        x: sellSignals.map(
            row => row.Date
        ),

        y: sellSignals.map(
            row => row.Close
        ),

        mode: "markers",

        name: "SELL",

        marker: {
            symbol: "triangle-down",
            size: 8,
            color: "#FF5252",
            line: {
                width: 1,
                color: "#FFFFFF"
            }

        }

    });


    // Plotting the price chart using Plotly
    Plotly.newPlot(
        ui.priceChart,
        traces,
        {
            autosize: true,
            margin: {
                l: 50,
                r: 20,
                t: 20,
                b: 40
            },
            paper_bgcolor: "transparent",
            plot_bgcolor: "transparent",
            font: {
                color: "#FFFFFF"
            },
            xaxis: {
                gridcolor: "#3b4456"
            },
            yaxis: {
                gridcolor: "#3b4456"
            },
            showlegend: true,
            dragmode: "pan"
        },
        {
            responsive: true,
            scrollZoom: true,
            displayModeBar: false
        }
    );

}


function renderEquityChart(analyticsHistory)
{

    const dates = analyticsHistory.map(row => row.Date);

    const portfolioValues = analyticsHistory.map(
        row => row["Portfolio Value"]
    );

    const buyHoldValues = analyticsHistory.map(
        row => row["Buy & Hold Value"]
    );

    const strategyTrace = {
        x: dates,
        y: portfolioValues,
        mode: "lines",
        name: "Strategy"
    };

    const benchmarkTrace = {
        x: dates,
        y: buyHoldValues,
        mode: "lines",
        name: "Buy & Hold",
        line: { dash: "dash" }
    };

    const layout = {

        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",

        margin: {
            l: 60,
            r: 20,
            t: 20,
            b: 70
        },

        xaxis: {

            title: "Date",

            gridcolor: "#3b4659",

            zeroline: false

        },

        yaxis: {

            title: "Portfolio Value",

            gridcolor: "#3b4659",

            zeroline: false

        },

        font: {

            color: "#FFFFFF"

        },

        dragmode: "pan"
    };

    Plotly.newPlot(
        ui.equityChart,
        [strategyTrace, benchmarkTrace],
        layout,
        {
            responsive: true,
            displayModeBar: false,
            scrollZoom: true
        }
    );
}


function renderDrawdownChart(analyticsHistory)
{
    const dates = analyticsHistory.map(
        row => row.Date
    );

    const drawdowns = analyticsHistory.map(
        row => row.Drawdown
    );

    const trace = {

        x: dates,

        y: drawdowns,

        mode: "lines",

        fill: "tozeroy",

        name: "Drawdown"

    };

    const layout = {

        paper_bgcolor: "rgba(0,0,0,0)",

        plot_bgcolor: "rgba(0,0,0,0)",

        margin: {
            l: 60,
            r: 20,
            t: 20,
            b: 70
        },

        xaxis: {

            title: "Date",

            gridcolor: "#3b4659",

            zeroline: false

        },

        yaxis: {

            title: "Drawdown",

            gridcolor: "#3b4659",

            zeroline: true,

            rangemode: "tozero"

        },

        font: {

            color: "#FFFFFF"

        },

        dragmode: "pan"

    };

    Plotly.newPlot(
        ui.drawdownChart,
        [trace],
        layout,
        {
            responsive: true,
            displayModeBar: false,
            scrollZoom: true
        }
    );
}