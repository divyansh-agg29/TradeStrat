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
    },

    kelly_criterion: {
        label: "Kelly Criterion",
        parameters: [
            {key: "win_rate", label: "Win Rate %", type: "number", default: 55, min: 0.1, max: 99.9, step: 0.1},
            {key: "win_loss_ratio", label: "Win/Loss Ratio", type: "number", default: 1.5, min: 0.01, step: 0.01},
            {key: "kelly_fraction", label: "Kelly Fraction", type: "number", default: 50, min: 0.1, max: 100, step: 0.1}
        ],

        toPayload(params) {
            return {
                win_rate: params.win_rate / 100,
                win_loss_ratio: params.win_loss_ratio,
                kelly_fraction: params.kelly_fraction / 100
            };
        },

        fromPayload(params) {
            return {
                win_rate: params.win_rate * 100,
                win_loss_ratio: params.win_loss_ratio,
                kelly_fraction: params.kelly_fraction * 100
            };
        },

        validate(params) {
            const errors = [];
            if (!params.win_rate || params.win_rate <= 0) {
                errors.push("Win Rate % must be greater than zero.");
            }
            if (params.win_rate >= 100) {
                errors.push("Win Rate % must be less than 100.");
            }
            if (!params.win_loss_ratio || params.win_loss_ratio <= 0) {
                errors.push("Win/Loss Ratio must be greater than zero.");
            }
            if (!params.kelly_fraction || params.kelly_fraction <= 0) {
                errors.push("Kelly Fraction must be greater than zero.");
            }
            if (params.kelly_fraction > 100) {
                errors.push("Kelly Fraction cannot exceed 100.");
            }
            return errors;
        }
    }

};
