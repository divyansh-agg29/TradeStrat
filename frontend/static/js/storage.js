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