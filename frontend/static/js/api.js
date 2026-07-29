"use strict";

const BACKTEST_ENDPOINT = "/backtest";


function buildBacktestRequest(configuration) {

    const risk = {};

    if (configuration.risk && configuration.risk.stopLossPercent !== "") {
        risk.stop_loss_enabled = true;
        risk.stop_loss_percent = Number(configuration.risk.stopLossPercent);
    }

    return {

        ticker: configuration.ticker,

        start_date: configuration.startDate,

        end_date: configuration.endDate,

        initial_capital: configuration.initialCapital,

        strategy: {

            type: configuration.strategy.type,

            parameters: configuration.strategy.parameters

        },

        risk: Object.keys(risk).length > 0 ? risk : undefined

    };

}


async function runBacktest(configuration) {

    const requestBody =buildBacktestRequest(configuration);

    console.log("API Request:",requestBody);

    const response = await fetch(
        BACKTEST_ENDPOINT,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestBody)
        }
    );


    const result = await response.json();

    if (!result.success) {

        throw new Error(
            result.error.message
        );

    }

    return result;
}