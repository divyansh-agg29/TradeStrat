"use strict";

const STRATEGY_REGISTRY = {

    sma_crossover: {
        label: "SMA Crossover",
        parameters: [
            {key: "short_period", label: "Short SMA", type: "number", default: 20, min: 1},
            {key: "long_period", label: "Long SMA", type: "number", default: 50, min: 1}
        ],

        validate(params) {
            const errors = [];
            if (params.short_period <= 0) {errors.push("Short SMA period must be positive.");}
            if (params.long_period <= 0) {errors.push("Long SMA period must be positive.");}
            if (params.short_period >= params.long_period) {errors.push("Short SMA period must be smaller than Long SMA period.");}
            return errors;
        }

    },

    ema_crossover: {
        label: "EMA Crossover",
        parameters: [
            {key: "short_period", label: "Short EMA", type: "number", default: 20, min: 1},
            {key: "long_period", label: "Long EMA", type: "number", default: 50, min: 1}
        ],

        validate(params) {
            const errors = [];
            if (params.short_period <= 0) {errors.push("Short EMA period must be positive.");}
            if (params.long_period <= 0) {errors.push("Long EMA period must be positive.");}
            if (params.short_period >= params.long_period) {errors.push("Short EMA period must be smaller than Long EMA period.");}
            return errors;
        }

    },

    macd_crossover: {
        label: "MACD Crossover",
        parameters: [
            {key: "short_period", label: "Short EMA", type: "number", default: 12, min: 1},
            {key: "long_period", label: "Long EMA", type: "number", default: 26, min: 1},
            {key: "signal_period", label: "Signal EMA", type: "number", default: 9, min: 1}
        ],

        validate(params) {
            const errors = [];
            if (params.short_period <= 0) {errors.push("Short EMA period must be positive.");}
            if (params.long_period <= 0) {errors.push("Long EMA period must be positive.");}
            if (params.signal_period <= 0) {errors.push("Signal EMA period must be positive.");}
            if (params.short_period >= params.long_period) {errors.push("Short EMA period must be smaller than Long EMA period.");}
            return errors;
        }

    }




};
