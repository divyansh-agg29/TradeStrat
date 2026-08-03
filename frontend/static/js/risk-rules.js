"use strict";

const STOP_LOSS_REGISTRY = {

    fixed_percentage: {
        label: "Fixed Percentage",
        parameters: [
            {key: "percent", label: "Stop Loss %", type: "number", default: 5, min: 0.1, step: 0.1}
        ],

        toPayload(params) {
            return {percent: params.percent / 100};
        },

        fromPayload(params) {
            return {percent: params.percent * 100};
        },

        validate(params) {
            const errors = [];
            if (!params.percent || params.percent <= 0) {
                errors.push("Stop Loss % must be greater than zero.");
            }
            return errors;
        }

    },

    fixed_price_offset: {
        label: "Fixed Price Offset",
        parameters: [
            {key: "offset", label: "Price Offset", type: "number", default: 5, min: 0.01, step: 0.01}
        ],

        toPayload(params) {
            return {offset: params.offset};
        },

        fromPayload(params) {
            return {offset: params.offset};
        },

        validate(params) {
            const errors = [];
            if (!params.offset || params.offset <= 0) {
                errors.push("Price Offset must be greater than zero.");
            }
            return errors;
        }
    },

    trailing_stop: {
        label: "Trailing Stop",
        parameters: [
            {key: "percent", label: "Trail %", type: "number", default: 5, min: 0.1, step: 0.1}
        ],

        toPayload(params) {
            return {percent: params.percent / 100};
        },

        fromPayload(params) {
            return {percent: params.percent * 100};
        },

        validate(params) {
            const errors = [];
            if (!params.percent || params.percent <= 0) {
                errors.push("Trail % must be greater than zero.");
            }
            return errors;
        }
    }

};
