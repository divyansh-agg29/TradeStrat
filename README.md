# TradeStrat
A web-based modular trading strategy analysis platform for backtesting, portfolio simulation and performance evaluation on historical stock market data.


## Features

- Historical market data download using Yahoo Finance
- Market data validation and cleaning
- Generic technical indicator engine
- SMA crossover strategy
- Portfolio simulation
- Performance analytics
- Risk metrics
- Trade statistics
- Interactive dashboard
- Plotly visualizations
- REST API

## Screenshots

<img src="images/image_1.png" alt="Alt text" width="600">
<br><br>
<img src="images/image_2.png" alt="Alt text" width="600">
<br><br>
<img src="images/image_3.png" alt="Alt text" width="600">
<br><br>
<img src="images/image_4.png" alt="Alt text" width="600">
<br><br>

## Technology Stack

| Category | Technologies |
|----------|--------------|
| **Backend** | Python, Flask |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Data Processing** | Pandas, NumPy |
| **Market Data** | Yahoo Finance (`yfinance`) |
| **Data Visualization** | Plotly, Plotly.js |
| **Testing** | pytest |


## Version History

### Version 1.0
Initial MVP release.

- Market Data Module
- Indicator Engine
- SMA indicator
- Strategy Engine
- SMA Crossover Strategy
- Portfolio Simulator
- Analytics Engine
- Portfolio Metrics, Risk Metrics, Trade Metrics, Price Chart, Equity Chart, Drawdown Chart, Trade History
- Backtest Service
- REST API
- Interactive Dashboard

### Version 1.1
Expanded strategy support and technical analysis capabilities.

- Added EMA, RSI and MACD indicators
- Added trading strategies: EMA crossover, MACD Crossover, RSI Mean Reversion
- Improved chart interaction: mouse-wheel zoom, drag to pan

### Version 1.2
Improved backtesting accuracy and overall user experience.

- Added automatic indicator warm-up period for more accurate recursive indicator calculations
- Added full-screen loading overlay during backtest execution
- Added user-friendly error modal for frontend and backend validation errors

### Version 1.3
Enhanced backtesting analytics with benchmark comparison and extended risk metrics.

- Added Buy & Hold benchmark comparison with passive equity curve overlay on the Equity Chart
- Added Benchmark Metrics panel displaying Buy & Hold Final Value, Buy & Hold Return, and Strategy Alpha
- Added Sortino Ratio and Calmar Ratio to Risk Metrics

### Version 1.4
Redesigned dashboard UI for compactness and practicality.

- Compacted KPI cards with reduced padding and font sizes
- Expanded KPI grid to 5 columns with Sortino Ratio and Alpha cards
- Reordered KPI cards into Portfolio Performance and Risk & Context rows
- Reduced chart heights and tightened section spacing across the dashboard
- Narrowed control panel sidebar from 360px to 260px
- Arranged Portfolio, Risk and Benchmark Metrics side-by-side in a 3-column layout
- Restructured Trade Statistics into uniform paired rows for better space utilisation
- Compacted metric rows and dashboard panel padding throughout