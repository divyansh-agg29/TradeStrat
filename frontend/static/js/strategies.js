"use strict";

const STRATEGY_REGISTRY = {

    sma_crossover: {
        label: "SMA Crossover",
        parameters: [
            {key: "short_period", label: "Short SMA", type: "number", default: 20, min: 1},
            {key: "long_period", label: "Long SMA", type: "number", default: 50, min: 1}
        ],
    },

    ema_crossover: {
        label: "EMA Crossover",
        parameters: [
            {key: "short_period", label: "Short EMA", type: "number", default: 20, min: 1},
            {key: "long_period", label: "Long EMA", type: "number", default: 50, min: 1}
        ],
    },

    macd_crossover: {
        label: "MACD Crossover",
        parameters: [
            {key: "short_period", label: "Short EMA", type: "number", default: 12, min: 1},
            {key: "long_period", label: "Long EMA", type: "number", default: 26, min: 1},
            {key: "signal_period", label: "Signal EMA", type: "number", default: 9, min: 1}
        ],
    },

    rsi_mean_reversion: {
        label: "RSI Mean Reversion",
        parameters: [
            {key: "rsi_period", label: "RSI Period", type: "number", default: 14, min: 1},
            {key: "overbought", label: "Overbought", type: "number", default: 70, min: 1},
            {key: "oversold", label: "Oversold", type: "number", default: 30, min: 1}
        ],
    }

};
