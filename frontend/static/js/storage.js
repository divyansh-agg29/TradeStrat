"use strict";

const STORAGE_KEY = "tradeStratConfiguration";

function saveConfiguration(configuration) {

    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(configuration)
    );

}

function loadConfiguration() {

    try {
        const savedConfiguration =
            localStorage.getItem(STORAGE_KEY);

        return savedConfiguration
            ? JSON.parse(savedConfiguration)
            : null;
    } catch (e) {
        console.warn("Failed to parse saved configuration, clearing corrupt data.", e);
        localStorage.removeItem(STORAGE_KEY);
        return null;
    }

}


const COMPARE_STORAGE_KEY = "tradeStratCompareConfiguration";

function saveCompareConfiguration(configuration) {

    localStorage.setItem(
        COMPARE_STORAGE_KEY,
        JSON.stringify(configuration)
    );

}

function loadCompareConfiguration() {

    try {
        const saved =
            localStorage.getItem(COMPARE_STORAGE_KEY);

        return saved
            ? JSON.parse(saved)
            : null;
    } catch (e) {
        console.warn("Failed to parse saved compare configuration, clearing corrupt data.", e);
        localStorage.removeItem(COMPARE_STORAGE_KEY);
        return null;
    }

}