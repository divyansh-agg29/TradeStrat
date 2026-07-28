"use strict";

const STORAGE_KEY = "tradeStratConfiguration";

function saveConfiguration(configuration) {

    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(configuration)
    );

}

function loadConfiguration() {

    const savedConfiguration =
        localStorage.getItem(STORAGE_KEY);

    if (!savedConfiguration) {

        return null;

    }

    return JSON.parse(savedConfiguration);

}


const COMPARE_STORAGE_KEY = "tradeStratCompareConfiguration";

function saveCompareConfiguration(configuration) {

    localStorage.setItem(
        COMPARE_STORAGE_KEY,
        JSON.stringify(configuration)
    );

}

function loadCompareConfiguration() {

    const saved =
        localStorage.getItem(COMPARE_STORAGE_KEY);

    if (!saved) {

        return null;

    }

    return JSON.parse(saved);

}