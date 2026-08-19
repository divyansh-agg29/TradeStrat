"use strict";

const BACKTEST_ENDPOINT = "/backtest";


function buildBacktestRequest(configuration) {

    const request = {

        ticker: configuration.ticker,

        start_date: configuration.startDate,

        end_date: configuration.endDate,

        initial_capital: configuration.initialCapital,

        interval: configuration.interval || "1d",

        strategy: {

            type: configuration.strategy.type,

            parameters: configuration.strategy.parameters

        }

    };

    const hasStopLoss = configuration.risk && configuration.risk.stopLossType;
    const hasTakeProfit = configuration.risk && configuration.risk.takeProfitType;

    if (hasStopLoss || hasTakeProfit) {
        request.risk = {};

        if (hasStopLoss) {
            request.risk.stop_loss_type = configuration.risk.stopLossType;
            request.risk.parameters = configuration.risk.parameters;
        }

        if (hasTakeProfit) {
            request.risk.take_profit_type = configuration.risk.takeProfitType;
            request.risk.take_profit_parameters = configuration.risk.takeProfitParameters;
        }
    }

    if (configuration.positionSizing && configuration.positionSizing.sizingType) {
        request.position_sizing = {
            sizing_type: configuration.positionSizing.sizingType,
            parameters: configuration.positionSizing.parameters,
        };
    }

    return request;

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