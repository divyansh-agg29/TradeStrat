"use strict";

function formatPercentage(value) {

    return `${value.toFixed(2)}%`;

}


const currencyFormatter = new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
});

function formatCurrency(value) {
    return currencyFormatter.format(value);
}


function formatNumber(value) {

    return value.toFixed(2);

}

function formatDate(dateString) {

    const date = new Date(dateString);

    return date.toLocaleDateString(
        "en-IN",
        {
            day: "2-digit",
            month: "short",
            year: "numeric"
        }
    );

}