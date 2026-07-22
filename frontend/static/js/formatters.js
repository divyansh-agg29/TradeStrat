"use strict";

function formatPercentage(value) {

    if (value === null || value === undefined) { return "N/A"; }
    return `${value.toFixed(2)}%`;

}


const currencyFormatter = new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
});

function formatCurrency(value) {
    if (value === null || value === undefined) { return "N/A"; }
    return currencyFormatter.format(value);
}


function formatNumber(value) {

    if (value === null || value === undefined) { return "N/A"; }
    return value.toFixed(2);

}

function formatByType(value, formatType) {

    switch (formatType) {
        case "percentage": return formatPercentage(value);
        case "currency": return formatCurrency(value);
        case "number": return formatNumber(value);
        case "integer": return value != null ? String(value) : "N/A";
        default: return String(value);
    }

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