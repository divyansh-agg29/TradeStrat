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

    }

};
