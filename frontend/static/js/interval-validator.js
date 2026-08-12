"use strict";

// Interval configuration and validation

const INTERVAL_CONFIG = {
    "1m": {
        displayName: "1 Minute",
        maxRangeDays: 7,
        maxLookbackDays: 30,
        useCase: "High-frequency day trading"
    },
    "5m": {
        displayName: "5 Minutes",
        maxRangeDays: 60,
        maxLookbackDays: 60,
        useCase: "Intraday swing trading"
    },
    "15m": {
        displayName: "15 Minutes",
        maxRangeDays: 60,
        maxLookbackDays: 60,
        useCase: "Short-term position trading"
    },
    "30m": {
        displayName: "30 Minutes",
        maxRangeDays: 60,
        maxLookbackDays: 60,
        useCase: "Intraday to multi-day strategies"
    },
    "1h": {
        displayName: "1 Hour",
        maxRangeDays: 730,
        maxLookbackDays: 730,
        useCase: "Multi-day swing trading"
    },
    "1d": {
        displayName: "1 Day",
        maxRangeDays: null,
        maxLookbackDays: null,
        useCase: "Traditional backtesting (default)"
    },
    "1wk": {
        displayName: "1 Week",
        maxRangeDays: null,
        maxLookbackDays: null,
        useCase: "Long-term trend following"
    },
    "1mo": {
        displayName: "1 Month",
        maxRangeDays: null,
        maxLookbackDays: null,
        useCase: "Very long-term strategies"
    }
};


function updateIntervalHint(intervalValue, hintElementId) {
    const config = INTERVAL_CONFIG[intervalValue];
    const hintElement = document.getElementById(hintElementId);
    
    if (!config || !hintElement) {
        return;
    }
    
    const parts = [];
    
    if (config.maxRangeDays) {
        parts.push(`Max range: ${config.maxRangeDays} days`);
    } else {
        parts.push("Unlimited range");
    }
    
    if (config.maxLookbackDays) {
        parts.push(`Data available: last ${config.maxLookbackDays} days`);
    } else {
        parts.push("Unlimited history");
    }
    
    hintElement.textContent = config.displayName + " — " + parts.join(", ");
}


function validateIntervalDateRange(interval, startDate, endDate) {
    const config = INTERVAL_CONFIG[interval];
    
    if (!config) {
        return {
            valid: false,
            error: `Invalid interval: ${interval}`
        };
    }
    
    const start = new Date(startDate);
    const end = new Date(endDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    // Check if dates are valid
    if (isNaN(start.getTime()) || isNaN(end.getTime())) {
        return {
            valid: false,
            error: "Invalid date format"
        };
    }
    
    // Check if start is before end
    if (start > end) {
        return {
            valid: false,
            error: "Start date must be before end date"
        };
    }
    
    // Check if dates are not in the future
    if (end > today) {
        return {
            valid: false,
            error: "End date cannot be in the future"
        };
    }
    
    // Check range size
    if (config.maxRangeDays) {
        const rangeDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
        
        if (rangeDays > config.maxRangeDays) {
            return {
                valid: false,
                error: `Date range too large for ${config.displayName}. Maximum: ${config.maxRangeDays} days, Requested: ${rangeDays} days. Try a larger interval like 5m or 1h.`
            };
        }
    }
    
    // Check lookback limit
    if (config.maxLookbackDays) {
        const lookbackDays = Math.ceil((today - start) / (1000 * 60 * 60 * 24));
        
        if (lookbackDays > config.maxLookbackDays) {
            const earliestDate = new Date(today);
            earliestDate.setDate(earliestDate.getDate() - config.maxLookbackDays);
            const earliestStr = earliestDate.toISOString().split('T')[0];
            
            return {
                valid: false,
                error: `Start date too far in the past for ${config.displayName}. Data only available from ${earliestStr} onwards.`
            };
        }
    }
    
    return { valid: true };
}


// Initialize interval change listeners
function initIntervalValidation() {
    const intervalSelect = document.getElementById("interval");
    const compareIntervalSelect = document.getElementById("compare-interval");
    
    if (intervalSelect) {
        intervalSelect.addEventListener("change", function() {
            updateIntervalHint(this.value, "interval-hint");
        });
        
        // Set initial hint
        updateIntervalHint(intervalSelect.value, "interval-hint");
    }
    
    if (compareIntervalSelect) {
        compareIntervalSelect.addEventListener("change", function() {
            updateIntervalHint(this.value, "compare-interval-hint");
        });
        
        // Set initial hint
        updateIntervalHint(compareIntervalSelect.value, "compare-interval-hint");
    }
}


// Add to DOMContentLoaded
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initIntervalValidation);
} else {
    initIntervalValidation();
}
