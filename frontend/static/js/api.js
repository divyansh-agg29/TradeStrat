"use strict";

const BACKTEST_ENDPOINT = "/backtest";


function buildBacktestRequest(configuration) {

    return {

        ticker: configuration.ticker,

        start_date: configuration.startDate,

        end_date: configuration.endDate,

        initial_capital: configuration.initialCapital,

        strategy: {

            type: configuration.strategy.type,

            parameters: {

                short_period:
                    configuration.strategy.shortPeriod,

                long_period:
                    configuration.strategy.longPeriod

            }

        }

    };

}


async function runBacktest(configuration) {

    const requestBody =
        buildBacktestRequest(configuration);

    console.log(
        "API Request:",
        requestBody
    );

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

    return await response.json();

}