"use strict";

const POSITION_SIZING_REGISTRY = {

    fixed_percentage: {
        label: "Fixed Percentage",
        parameters: [
            {key: "percent", label: "Portfolio %", type: "number", default: 25, min: 0.1, max: 100, step: 0.1}
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
                errors.push("Portfolio % must be greater than zero.");
            }
            if (params.percent > 100) {
                errors.push("Portfolio % cannot exceed 100.");
            }
            return errors;
        }
    },

    fixed_amount: {
        label: "Fixed Amount",
        parameters: [
            {key: "amount", label: "Amount", type: "number", default: 10000, min: 1, step: 1}
        ],

        toPayload(params) {
            return {amount: params.amount};
        },

        fromPayload(params) {
            return {amount: params.amount};
        },

        validate(params) {
            const errors = [];
            if (!params.amount || params.amount <= 0) {
                errors.push("Amount must be greater than zero.");
            }
            return errors;
        }
    },

    fixed_shares: {
        label: "Fixed Shares",
        parameters: [
            {key: "shares", label: "Shares", type: "number", default: 100, min: 1, step: 1}
        ],

        toPayload(params) {
            return {shares: params.shares};
        },

        fromPayload(params) {
            return {shares: params.shares};
        },

        validate(params) {
            const errors = [];
            if (!params.shares || params.shares <= 0) {
                errors.push("Shares must be greater than zero.");
            }
            return errors;
        }
    },

    risk_based: {
        label: "Risk-Based",
        parameters: [
            {key: "risk_percent", label: "Risk %", type: "number", default: 2, min: 0.1, max: 100, step: 0.1}
        ],

        toPayload(params) {
            return {risk_percent: params.risk_percent / 100};
        },

        fromPayload(params) {
            return {risk_percent: params.risk_percent * 100};
        },

        validate(params) {
            const errors = [];
            if (!params.risk_percent || params.risk_percent <= 0) {
                errors.push("Risk % must be greater than zero.");
            }
            if (params.risk_percent > 100) {
                errors.push("Risk % cannot exceed 100.");
            }
            return errors;
        }
    }

};
