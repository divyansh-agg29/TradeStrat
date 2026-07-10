"use strict";

document.addEventListener(
    "DOMContentLoaded",
    initializeApplication
);

function initializeApplication() {

    console.log(
        "Trading Dashboard Initialized"
    );

    populateStrategyDropdown();

    onStrategyChanged();

    restorePreviousConfiguration();

    registerEventListeners();

}

function restorePreviousConfiguration() {

    const configuration =
        loadConfiguration();

    if (!configuration) {

        return;

    }

    populateConfigurationForm(configuration);

}