"use strict";

const KPI_TOOLTIPS = {

    final_portfolio_value: {
        description: "Total portfolio value at the end of the backtest period.",
        preference: "Higher is better.",
    },

    total_return: {
        description: "Percentage gain or loss on the initial capital.",
        preference: "Higher is better.",
    },

    cagr: {
        description: "Compound Annual Growth Rate — annualized return over the backtest period.",
        preference: "Higher is better.",
        ranges: [
            "Below 5% → Poor",
            "5% – 10% → Average",
            "10% – 20% → Good",
            "Above 20% → Excellent",
        ],
    },

    win_rate: {
        description: "Percentage of trades that were profitable.",
        preference: "Higher is better, but depends on risk/reward ratio.",
    },

    profit_factor: {
        description: "Ratio of gross profits to gross losses.",
        preference: "Higher is better.",
        ranges: [
            "Below 1.0 → Losing strategy",
            "1.0 – 1.5 → Average",
            "1.5 – 2.0 → Good",
            "Above 2.0 → Excellent",
        ],
    },

    sharpe_ratio: {
        description: "Risk-adjusted return per unit of total volatility.",
        preference: "Higher is better.",
        ranges: [
            "Below 0.5 → Poor",
            "0.5 – 1.0 → Average",
            "1.0 – 1.5 → Good",
            "Above 1.5 → Excellent",
        ],
    },

    sortino_ratio: {
        description: "Risk-adjusted return considering only downside volatility.",
        preference: "Higher is better.",
        ranges: [
            "Below 0.5 → Poor",
            "0.5 – 1.0 → Average",
            "1.0 – 1.5 → Good",
            "Above 1.5 → Excellent",
        ],
    },

    maximum_drawdown: {
        description: "Largest peak-to-trough decline during the backtest.",
        preference: "Lower is better.",
        ranges: [
            "Below 5% → Excellent",
            "5% – 15% → Good",
            "15% – 25% → Average",
            "Above 25% → Poor",
        ],
    },

    total_trades: {
        description: "Number of completed round-trip trades.",
        preference: "Depends on strategy type.",
    },

    alpha: {
        description: "Strategy return minus Buy & Hold return.",
        preference: "Positive is better — indicates outperformance.",
        ranges: [
            "Below -5% → Poor",
            "-5% – 0% → Average",
            "0% – 10% → Good",
            "Above 10% → Excellent",
        ],
    },

};


function initKpiTooltips() {

    const tooltip = document.createElement("div");
    tooltip.className = "kpi-tooltip";
    tooltip.style.display = "none";
    document.body.appendChild(tooltip);

    document.querySelectorAll(".kpi-info-icon").forEach(function (icon) {

        icon.addEventListener("mouseenter", function (e) {

            const key = icon.getAttribute("data-kpi");
            const data = KPI_TOOLTIPS[key];

            if (!data) return;

            let html = "<strong>" + data.description + "</strong>";
            html += "<br>" + data.preference;

            if (data.ranges) {
                html += "<br><br>";
                for (const range of data.ranges) {
                    html += range + "<br>";
                }
            }

            tooltip.innerHTML = html;
            tooltip.style.display = "block";

            const rect = icon.getBoundingClientRect();
            tooltip.style.left = rect.left + "px";
            tooltip.style.top = (rect.bottom + 8) + "px";

        });

        icon.addEventListener("mouseleave", function () {
            tooltip.style.display = "none";
        });

    });

}
