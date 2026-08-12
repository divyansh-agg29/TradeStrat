"use strict";

/**
 * Backend-driven chart renderer.
 *
 * Maps semantic trace types from the backend chart specification
 * to Plotly trace objects.  The backend decides *what* to display;
 * this module decides *how* it looks.
 */


// ── Helpers ─────────────────────────────────────────────────


function isIntradayData(chartSpec) {
    // Detect intraday data by checking if timestamps have non-midnight times.
    // Daily data uses isoformat() which produces "2024-01-01T00:00:00" (midnight).
    // Intraday data has actual times like "2024-01-01T09:15:00+05:30".
    
    if (!chartSpec || !chartSpec.traces || chartSpec.traces.length === 0) {
        return false;
    }
    
    for (var i = 0; i < chartSpec.traces.length; i++) {
        var trace = chartSpec.traces[i];
        if (trace.x && trace.x.length > 1) {
            // Check a few timestamps (skip first in case it's an edge case)
            for (var j = 1; j < Math.min(trace.x.length, 5); j++) {
                var ts = String(trace.x[j]);
                // Extract time portion after 'T' or space
                var timeMatch = ts.match(/[T ]\s*(\d{2}):(\d{2})/);
                if (timeMatch) {
                    var hours = parseInt(timeMatch[1], 10);
                    var minutes = parseInt(timeMatch[2], 10);
                    // Non-midnight time means intraday data
                    if (hours !== 0 || minutes !== 0) {
                        return true;
                    }
                }
            }
        }
    }
    
    return false;
}


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
        xaxis: {
            rangeslider: {visible: false},
            gridcolor: "#3b4659"
        },
        yaxis: {gridcolor: "#3b4659"}
    },

    equity_chart: {
        xaxis: {
            title: "Date",
            gridcolor: "#3b4659",
            zeroline: false
        },
        yaxis: {title: "Portfolio Value", gridcolor: "#3b4659", zeroline: false},
        margin: {l: 60, r: 20, t: 20, b: 70}
    },

    drawdown_chart: {
        xaxis: {
            title: "Date",
            gridcolor: "#3b4659",
            zeroline: false
        },
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

    var hasSubplots = chartKey === "price_chart" && 
                      chartSpec.subplots && 
                      chartSpec.subplots.length > 1;

    if (hasSubplots) {
        renderPriceChartWithSubplots(containerId, chartSpec, activeView);
        return;
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

    const layout = buildLayout(chartKey, chartSpec);

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


function renderPriceChartWithSubplots(containerId, chartSpec, activeView) {

    var subplots = chartSpec.subplots;
    var numRows = subplots.length;

    var subplotIdToRow = {};
    subplots.forEach(function(subplot, index) {
        subplotIdToRow[subplot.id] = index + 1;
    });

    var totalHeight = subplots.reduce(function(sum, s) {
        return sum + s.height_ratio;
    }, 0);

    var rowHeights = subplots.map(function(s) {
        return s.height_ratio / totalHeight;
    });

    var traces = [];

    chartSpec.traces.forEach(function(traceSpec, index) {

        var plotlyTrace = buildPlotlyTrace(traceSpec, "price_chart");

        var subplotId = traceSpec.subplot || "main";
        var row = subplotIdToRow[subplotId] || 1;

        if (row === 1) {
            plotlyTrace.yaxis = "y";
            plotlyTrace.xaxis = "x";
        } else {
            plotlyTrace.yaxis = "y" + row;
            plotlyTrace.xaxis = "x";
        }

        if (traceSpec.group) {
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

    var layout = buildSubplotLayout(subplots, rowHeights, chartSpec);

    Plotly.newPlot(
        document.getElementById(containerId),
        traces,
        layout,
        CHART_CONFIG
    );

}


function buildSubplotLayout(subplots, rowHeights, chartSpec) {

    var isIntraday = isIntradayData(chartSpec);

    var layout = {
        autosize: true,
        paper_bgcolor: "transparent",
        plot_bgcolor: "transparent",
        font: {color: "#FFFFFF"},
        showlegend: true,
        dragmode: "pan",
        margin: {l: 50, r: 20, t: 20, b: 40},
        grid: {
            rows: subplots.length,
            columns: 1,
            pattern: "independent",
            roworder: "top to bottom"
        }
    };

    var verticalSpacing = 0.03;
    var availableHeight = 1 - (verticalSpacing * (subplots.length - 1));

    var currentY = 1;

    subplots.forEach(function(subplot, index) {

        var height = rowHeights[index] * availableHeight;
        var yAxisKey = index === 0 ? "yaxis" : "yaxis" + (index + 1);
        var xAxisKey = index === 0 ? "xaxis" : "xaxis" + (index + 1);

        var domain = [currentY - height, currentY];
        currentY = currentY - height - verticalSpacing;

        layout[yAxisKey] = {
            domain: domain,
            gridcolor: "#3b4659",
            zeroline: false,
            anchor: index === 0 ? "x" : "x" + (index + 1)
        };

        if (subplot.y_range) {
            layout[yAxisKey].range = subplot.y_range;
            layout[yAxisKey].fixedrange = true;
        }

        layout[xAxisKey] = {
            gridcolor: "#3b4659",
            anchor: index === 0 ? "y" : "y" + (index + 1),
            matches: index === 0 ? undefined : "x"
        };

        // Only add rangebreaks for intraday data
        if (isIntraday) {
            layout[xAxisKey].rangebreaks = [
                {bounds: ["sat", "mon"]},
                {bounds: [15.5, 9.25], pattern: "hour"}
            ];
        }

        if (index === 0) {
            layout[xAxisKey].rangeslider = {visible: false};
        } else {
            layout[xAxisKey].showticklabels = false;
        }

    });

    return layout;

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


function buildLayout(chartKey, chartSpec) {

    var layout = {};
    var isIntraday = isIntradayData(chartSpec);

    for (var key in CHART_LAYOUT_BASE) {
        layout[key] = CHART_LAYOUT_BASE[key];
    }

    var overrides = CHART_LAYOUT_OVERRIDES[chartKey];

    if (overrides) {
        for (var key in overrides) {
            if (key === 'xaxis' && layout.xaxis) {
                // Merge xaxis properties
                layout.xaxis = Object.assign({}, layout.xaxis, overrides.xaxis);
            } else {
                layout[key] = overrides[key];
            }
        }
    }

    // Add rangebreaks only for intraday data
    if (isIntraday && layout.xaxis) {
        layout.xaxis.rangebreaks = [
            {bounds: ["sat", "mon"]},
            {bounds: [15.5, 9.25], pattern: "hour"}
        ];
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
