"use strict";

function renderDashboard(response) {

    const data = response.data;

    renderKPICards(data.kpi_cards);

    renderPortfolioMetrics(data.portfolio_metrics);

    renderRiskMetrics(data.risk_metrics);

    renderBenchmarkMetrics(data.benchmark_metrics);

    renderTradeStatistics(data.trade_metrics);

    renderCharts(data);

    renderTradeHistory(data.trade_history);

}

function renderKPICards(kpiCards) {

    for (const [key, kpi] of Object.entries(kpiCards)) {

        const elementId = "kpi-" + key.replace(/_/g, "-");
        const el = document.getElementById(elementId);

        if (!el) continue;

        el.textContent = formatByType(kpi.value, kpi.format_type);

        el.className = "kpi-value";

        if (kpi.interpretation) {
            el.classList.add("kpi-" + kpi.interpretation);
        }

    }

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

    renderChartFromSpec("price-chart", data.charts.price_chart, "price_chart");
    renderChartFromSpec("equity-chart", data.charts.equity_chart, "equity_chart");
    renderChartFromSpec("drawdown-chart", data.charts.drawdown_chart, "drawdown_chart");

}


function renderTradeHistory(trades) {

    ui.tradeHistoryBody.innerHTML = "";

    if (trades.length === 0) {
        ui.tradeHistoryBody.innerHTML = '<tr><td colspan="12" class="empty-table">No trades were executed during this period.</td></tr>';
        return;
    }

    for (const trade of trades) {

        const row = document.createElement("tr");

        const exitReason = trade.exit_reason;

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
            <td>${exitReason}</td>
            <td>${trade.num_entries || 1}</td>
        `;

        ui.tradeHistoryBody.appendChild(row);

    }

}
