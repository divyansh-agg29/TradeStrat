"use strict";

// Registry data populated by loadRegistries().
// Consumers (ui.js, compare.js) access these after initialization.

var STRATEGY_REGISTRY = {};
var STOP_LOSS_REGISTRY = {};
var TAKE_PROFIT_REGISTRY = {};
var POSITION_SIZING_REGISTRY = {};


function _buildValidate(params) {
    // Build a generic validate function from parameter min/max constraints.
    // Values may be in API scale (post-toPayload), so we adjust thresholds
    // by display_scale when present.
    // Cross-field rules are validated server-side only.
    return function validate(values) {
        const errors = [];
        for (const param of params) {
            const val = values[param.key];
            var scale = param.display_scale || 1;
            if (param.min !== undefined && val < param.min / scale) {
                errors.push(param.label + " must be at least " + param.min + ".");
            }
            if (param.max !== undefined && val > param.max / scale) {
                errors.push(param.label + " must be at most " + param.max + ".");
            }
        }
        return errors;
    };
}


function _buildToPayload(params) {
    // Build a toPayload function that divides display values by display_scale.
    return function toPayload(values) {
        const result = {};
        for (const param of params) {
            const val = values[param.key];
            result[param.key] = param.display_scale ? val / param.display_scale : val;
        }
        return result;
    };
}


function _buildFromPayload(params) {
    // Build a fromPayload function that multiplies API values by display_scale.
    return function fromPayload(values) {
        const result = {};
        for (const param of params) {
            const val = values[param.key];
            result[param.key] = param.display_scale ? val * param.display_scale : val;
        }
        return result;
    };
}


function _arrayToRegistry(entries) {
    // Convert [{key, label, parameters}, ...] to {key: {label, parameters, validate, toPayload, fromPayload}, ...}
    const registry = {};
    for (const entry of entries) {
        registry[entry.key] = {
            label: entry.label,
            parameters: entry.parameters,
            validate: _buildValidate(entry.parameters),
            toPayload: _buildToPayload(entry.parameters),
            fromPayload: _buildFromPayload(entry.parameters),
        };
    }
    return registry;
}


async function loadRegistries() {
    const response = await fetch("/registries");

    if (!response.ok) {
        throw new Error("Failed to load registries (HTTP " + response.status + ")");
    }

    const data = await response.json();

    STRATEGY_REGISTRY = _arrayToRegistry(data.strategies || []);
    STOP_LOSS_REGISTRY = _arrayToRegistry(data.stop_loss || []);
    TAKE_PROFIT_REGISTRY = _arrayToRegistry(data.take_profit || []);
    POSITION_SIZING_REGISTRY = _arrayToRegistry(data.position_sizing || []);
}
