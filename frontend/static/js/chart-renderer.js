"use strict";

/**
 * Backend-driven chart renderer.
 *
 * Maps semantic trace types from the backend chart specification
 * to Plotly trace objects.  The backend decides *what* to display;
 * this module decides *how* it looks.
 */


// ── Style Registry ──────────────────────────────────────────


const TRACE_STYLE_DEFAULTS = {

    line: {
        mode: "lines",
        line: {color: "#2196F3", width: 2}
    },

    indicator_line: {
        mode: "lines",
        line: {width: 1.5}
    },

    benchmark_line: {
        mode: "lines",
        line: {dash: "dash", color: "#9E9E9E"}
    },

    area: {
        mode: "lines",
        fill: "tozeroy"
    }

};


const SIGNAL_MARKER_STYLES = {

    buy: {
        symbol: "triangle-up",
        color: "#00E676",
        size: 10,
        line: {width: 2, color: "#FFFFFF"}
    },

    sell: {
        symbol: "triangle-down",
        color: "#FF5252",
        size: 10,
        line: {width: 2, color: "#FFFFFF"}
    }

};


const EXECUTION_MARKER_STYLES = {

    buy: {
        symbol: "triangle-up",
        color: "#00E676",
        size: 10,
        line: {width: 2, color: "#FFFFFF"}
    },

    sell_signal: {
        symbol: "triangle-down",
        color: "#FF5252",
        size: 10,
        line: {width: 2, color: "#FFFFFF"}
    },

    stop_loss: {
        symbol: "x",
        color: "#FF1744",
        size: 10,
        line: {width: 2, color: "#FF1744"}
    },

    take_profit: {
        symbol: "star",
        color: "#FFD700",
        size: 10,
        line: {width: 1, color: "#FFFFFF"}
    }

};


// ── Chart Layout Presets ────────────────────────────────────


const CHART_LAYOUT_BASE = {
    autosize: true,
    paper_bgcolor: "transparent",
    plot_bgcolor: "transparent",
    font: {color: "#FFFFFF"},
    xaxis: {gridcolor: "#3b4456"},
    yaxis: {gridcolor: "#3b4456"},
    showlegend: true,
    dragmode: "pan",
    margin: {l: 50, r: 20, t: 20, b: 40}
};


const CHART_LAYOUT_OVERRIDES = {

    price_chart: {
        xaxis: {rangeslider: {visible: false}, gridcolor: "#3b4659"},
        yaxis: {gridcolor: "#3b4659"}
    },

    equity_chart: {
        xaxis: {title: "Date", gridcolor: "#3b4659", zeroline: false},
        yaxis: {title: "Portfolio Value", gridcolor: "#3b4659", zeroline: false},
        margin: {l: 60, r: 20, t: 20, b: 70}
    },

    drawdown_chart: {
        xaxis: {title: "Date", gridcolor: "#3b4659", zeroline: false},
        yaxis: {title: "Drawdown", gridcolor: "#3b4659", zeroline: true, rangemode: "tozero"},
        margin: {l: 60, r: 20, t: 20, b: 70}
    }

};


const CHART_CONFIG = {
    responsive: true,
    scrollZoom: true,
    displayModeBar: false
};


// ── Public API ──────────────────────────────────────────────


var _priceChartTraceGroups = {};
var _priceChartContainerId = null;
var _priceChartSpec = null;
var _priceChartType = "candlestick";


function renderChartFromSpec(containerId, chartSpec, chartKey) {

    if (!chartSpec || !chartSpec.traces) {
        console.warn("No chart spec for", chartKey);
        return;
    }

    var activeView = "executions";

    if (chartKey === "price_chart") {
        _priceChartContainerId = containerId;
        _priceChartTraceGroups = {};
        _priceChartSpec = chartSpec;

        var chartTypeSelect = document.getElementById("price-chart-type");
        if (chartTypeSelect) {
            _priceChartType = chartTypeSelect.value;
        }

        var toggleContainer = document.getElementById("price-chart-view-toggle");
        if (toggleContainer) {
            var activeBtn = toggleContainer.querySelector(".view-toggle-btn.active");
            if (activeBtn) {
                activeView = activeBtn.dataset.view;
            }
        }
    }

    const traces = [];

    chartSpec.traces.forEach(function(traceSpec, index) {

        var plotlyTrace = buildPlotlyTrace(traceSpec, chartKey);

        if (chartKey === "price_chart" && traceSpec.group) {
            if (!_priceChartTraceGroups[traceSpec.group]) {
                _priceChartTraceGroups[traceSpec.group] = [];
            }
            _priceChartTraceGroups[traceSpec.group].push(traces.length);

            if (traceSpec.group !== activeView) {
                plotlyTrace.visible = false;
            }
        }

        traces.push(plotlyTrace);

    });

    const layout = buildLayout(chartKey);

    Plotly.newPlot(
        document.getElementById(containerId),
        traces,
        layout,
        CHART_CONFIG
    );

}


function onChartTypeChange(chartType) {

    _priceChartType = chartType;

    if (_priceChartSpec && _priceChartContainerId) {
        renderChartFromSpec(_priceChartContainerId, _priceChartSpec, "price_chart");
    }

}


function togglePriceChartView(view) {

    if (!_priceChartContainerId) {
        return;
    }

    var chartDiv = document.getElementById(_priceChartContainerId);

    if (!chartDiv || !chartDiv.data) {
        return;
    }

    var updates = {};

    for (var group in _priceChartTraceGroups) {
        var indices = _priceChartTraceGroups[group];
        var visible = (group === view);

        for (var i = 0; i < indices.length; i++) {
            updates[indices[i]] = visible;
        }
    }

    var traceIndices = [];
    var visibilities = [];

    for (var idx in updates) {
        traceIndices.push(parseInt(idx));
        visibilities.push(updates[idx]);
    }

    Plotly.restyle(
        chartDiv,
        {visible: visibilities},
        traceIndices
    );

}


// ── Trace Builder ───────────────────────────────────────────


function buildPlotlyTrace(spec, chartKey) {

    if (spec.type === "execution_marker" || spec.type === "signal_marker") {
        return buildMarkerTrace(spec);
    }

    if (spec.type === "candlestick") {
        return buildPriceTrace(spec, chartKey);
    }

    var style = TRACE_STYLE_DEFAULTS[spec.type];

    if (!style) {
        style = TRACE_STYLE_DEFAULTS.line;
    }

    var trace = {
        x: spec.x,
        y: spec.y,
        name: spec.name
    };

    for (var key in style) {
        trace[key] = style[key];
    }

    return trace;

}


function buildPriceTrace(spec, chartKey) {

    if (chartKey === "price_chart" && _priceChartType !== "candlestick") {
        var columnMap = {
            "line_open": {data: spec.open, name: "Open"},
            "line_high": {data: spec.high, name: "High"},
            "line_low": {data: spec.low, name: "Low"},
            "line_close": {data: spec.close, name: "Close"}
        };

        var selected = columnMap[_priceChartType] || columnMap["line_close"];

        return {
            x: spec.x,
            y: selected.data,
            name: selected.name,
            mode: "lines",
            line: {color: "#2196F3", width: 2}
        };
    }

    return buildCandlestickTrace(spec);

}


function buildCandlestickTrace(spec) {

    return {
        type: "candlestick",
        x: spec.x,
        open: spec.open,
        high: spec.high,
        low: spec.low,
        close: spec.close,
        name: spec.name,
        increasing: {line: {color: "#26A69A"}, fillcolor: "rgba(38, 166, 154, 0.7)"},
        decreasing: {line: {color: "#EF5350"}, fillcolor: "rgba(239, 83, 80, 0.7)"}
    };

}


function buildMarkerTrace(spec) {

    var markerStyle;

    if (spec.type === "signal_marker") {
        markerStyle = SIGNAL_MARKER_STYLES[spec.category];
    } else {
        markerStyle = EXECUTION_MARKER_STYLES[spec.category];
    }

    if (!markerStyle) {
        markerStyle = {
            symbol: "circle",
            color: "#FFFFFF",
            size: 8,
            line: {width: 1, color: "#FFFFFF"}
        };
    }

    return {
        x: spec.x,
        y: spec.y,
        mode: "markers",
        name: spec.name,
        marker: markerStyle
    };

}


// ── Layout Builder ──────────────────────────────────────────


function buildLayout(chartKey) {

    var layout = {};

    for (var key in CHART_LAYOUT_BASE) {
        layout[key] = CHART_LAYOUT_BASE[key];
    }

    var overrides = CHART_LAYOUT_OVERRIDES[chartKey];

    if (overrides) {
        for (var key in overrides) {
            layout[key] = overrides[key];
        }
    }

    return layout;

}


// ── View Toggle Handler ─────────────────────────────────────


function onViewToggle(button) {

    var view = button.dataset.view;

    var container = button.parentElement;
    var buttons = container.querySelectorAll(".view-toggle-btn");

    buttons.forEach(function(btn) {
        btn.classList.remove("active");
    });

    button.classList.add("active");

    togglePriceChartView(view);

}
