# ASR Portfolio Tracker

## Project Description
This project is a command-line portfolio tracker built in Python using an MVC architecture.

The application allows users to:
- add assets to a portfolio
- inspect current and historical market prices
- visualize price series
- view portfolio summaries and portfolio calculations
- run 15-year portfolio simulations with 100,000 Monte Carlo paths

The project was developed by Daan Stuijfzand for the a.s.r. Vermogensbeheer Portfolio Tracker assignment.

## Features
- Add assets with:
  - ticker
  - sector
  - asset class
  - quantity
  - purchase price
  - purchase date
- Automatic JSON save/load of the portfolio
- Show current and historical price data for a ticker
- Plot price graphs for:
  - a single ticker
  - multiple tickers
- View portfolio summary including:
  - asset name
  - sector
  - asset class
  - quantity
  - purchase price
  - transaction value
  - current value
- View portfolio calculations including:
  - total transaction value
  - total current value
  - per-asset contribution breakdown
  - relative weights by sector and asset class
  - Sharpe Ratio
  - Maximum Drawdown
- Run a 15-year portfolio simulation with 100,000 simulated paths using:
  - portfolio-level Geometric Brownian Motion (GBM)
  - correlated multi-asset simulation
- Display simulation summary statistics and simulation path graphs
- Base currency support with FX conversion:
  - historical FX conversion for transaction values based on purchase date
  - current FX conversion for current values

## Project Structure
```text
asr-portfolio-tracker/
├── controllers/
│   └── portfolio_controller.py
├── data/
│   └── portfolio.json
├── models/
│   ├── asset.py
│   └── portfolio.py
├── views/
│   ├── chart_view.py
│   └── table_view.py
├── main.py
├── requirements.txt
└── README.md
```

## MVC Architecture
The project follows the Model-View-Controller design pattern:

- **Model**
  - stores assets and portfolio data
  - retrieves market data
  - performs portfolio calculations
  - handles FX conversion
  - runs the simulation models

- **View**
  - renders terminal tables using `rich`
  - renders charts using `matplotlib`

- **Controller**
  - handles CLI user interaction
  - connects user input to model logic and views

## Installation

### 1. Clone the repository
```bash
git clone <your-repository-url>
cd asr-portfolio-tracker
```
### 2. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Run the Application
```bash
python3 main.py
```

## Menu Options
1. Add asset  
2. View portfolio summary  
3. Show current and historical price  
4. Plot price graph  
5. Show portfolio calculations  
6. Run 15-year portfolio simulation  
7. Exit  

When selecting option 6, the user can choose between:
1. **Portfolio-level GBM**
2. **Correlated multi-asset simulation**

## Currency Handling
The portfolio uses a **base currency**, which is currently set to **USD** by default.

- Asset prices are retrieved in their native trading currency
- Transaction values are converted to the base currency using a historical FX rate at the purchase date
- Current values are converted to the base currency using the latest FX rate

This allows the application to handle mixed-currency portfolios more realistically than simply summing raw native prices.

## Simulation Models

### 1. Portfolio-Level GBM
This model estimates portfolio-level expected return and volatility from historical monthly returns and simulates one aggregate portfolio process using Geometric Brownian Motion.

### 2. Correlated Multi-Asset Simulation
This model estimates:
- historical monthly mean returns per asset
- the covariance matrix across assets

It then simulates correlated monthly asset returns and aggregates them into a portfolio value path. This is a more advanced simulation than the portfolio-level GBM because it explicitly incorporates asset interactions through correlation.

## Simulation Output
Both simulation models display:
- initial portfolio value
- estimated annual return
- estimated annual volatility
- expected ending value
- median ending value
- 5th percentile ending value
- 95th percentile ending value
- VaR (95%)
- simulation path graph

## Additional Metrics
The application also calculates:
- **Sharpe Ratio**
- **Maximum Drawdown**

These are shown in the portfolio calculations view.

## Assumptions and Limitations
- Purchase price is assumed to be entered in the asset’s native trading currency
- Historical FX conversion uses a small window around the purchase date and takes the first available FX close in a small window around the purchase date
- Price graphs show native asset prices, not normalized returns
- Multi-ticker price graphs may include assets quoted in different currencies
- The simulations are based on historical monthly returns and simplified distributional assumptions
- The GBM model is a simplification of real-world market dynamics

## Libraries Used
- `yfinance`
- `pandas`
- `numpy`
- `matplotlib`
- `rich`

## Notes
The file `data/portfolio.json` is used for local persistence so that assets remain available between sessions.

## Assignment Coverage
This project was built to cover the main requirements of the a.s.r. Vermogensbeheer assignment, including:
- asset input and portfolio tracking
- current and historical price retrieval
- graphing of individual and multiple tickers
- portfolio overview and calculations
- 15-year simulation with 100,000 paths
- MVC architecture
- Git version control
- dependency management via `requirements.txt`