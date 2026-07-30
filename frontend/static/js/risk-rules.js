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

    absolute_price: {
        label: "Absolute Price",
        parameters: [
            {key: "price", label: "Stop Price", type: "number", default: 0, min: 0.01, step: 0.01}
        ],

        toPayload(params) {
            return {price: params.price};
        },

        fromPayload(params) {
            return {price: params.price};
        },

        validate(params) {
            const errors = [];
            if (!params.price || params.price <= 0) {
                errors.push("Stop Price must be greater than zero.");
            }
            return errors;
        }

    }

};
