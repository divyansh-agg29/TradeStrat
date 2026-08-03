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

    populateStopLossDropdown();

    populateTakeProfitDropdown();

    onStrategyChanged();

    restorePreviousConfiguration();

    registerEventListeners();

    initKpiTooltips();

    initTabSwitching();

    initCompareForm();

}

function initTabSwitching() {

    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    tabButtons.forEach(function(btn) {

        btn.addEventListener("click", function() {

            const targetTab = btn.dataset.tab;

            // Deactivate all tabs
            tabButtons.forEach(function(b) { b.classList.remove("active"); });
            tabContents.forEach(function(c) { c.classList.remove("active"); });

            // Activate selected tab
            btn.classList.add("active");
            document.getElementById(targetTab + "-tab-content").classList.add("active");

        });

    });

}

function restorePreviousConfiguration() {

    const configuration =
        loadConfiguration();

    if (!configuration) {

        return;

    }

    populateConfigurationForm(configuration);

}