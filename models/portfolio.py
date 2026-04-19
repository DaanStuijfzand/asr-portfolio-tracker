import numpy as np
import pandas as pd
import yfinance as yf
import json
from models.asset import Asset
from dataclasses import asdict
from pathlib import Path


class Portfolio:
    """
    Represents an investment portfolio containing multiple assets.
    Handles storage and basic portfolio calculations.
    """

    def __init__(self, base_currency: str = "USD"):
        self.assets = []
        self.base_currency = base_currency

    def add_asset(self, asset: Asset) -> None:
        """
        Adds an Asset object to the portfolio.
        """
        self.assets.append(asset)

    def get_assets(self) -> list[Asset]:
        """
        Returns all assets in the portfolio.
        """
        return self.assets
    
    def get_asset_currency(self, ticker: str) -> str:
        """
        Fetches the trading currency of an asset ticker.
        Falls back to the portfolio base currency if unavailable.
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            return info.get("currency", self.base_currency)
        except Exception:
            return self.base_currency

    def get_current_fx_rate(self, from_currency: str, to_currency: str) -> float | None:
        """
        Fetches the latest FX conversion rate from one currency to another.
        Returns 1.0 if both currencies are the same.
        """
        if from_currency == to_currency:
            return 1.0

        try:
            fx_ticker = f"{from_currency}{to_currency}=X"
            data = yf.Ticker(fx_ticker).history(period="5d")

            if data.empty:
                return None

            return float(data["Close"].iloc[-1])
        except Exception:
            return None

    def get_historical_fx_rate(self, from_currency: str, to_currency: str, date: str) -> float | None:
        """
        Fetches the FX conversion rate around a given historical date.
        Uses a small window and takes the last available close on or after the date.
        Returns 1.0 if both currencies are the same.
        """
        if from_currency == to_currency:
            return 1.0

        try:
            start = pd.to_datetime(date)
            end = start + pd.Timedelta(days=7)

            fx_ticker = f"{from_currency}{to_currency}=X"
            data = yf.Ticker(fx_ticker).history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))

            if data.empty:
                return None

            return float(data["Close"].iloc[0])
        except Exception:
            return None

    def convert_amount_current_fx(self, amount: float, from_currency: str, to_currency: str) -> float | None:
        """
        Converts an amount using the latest FX rate.
        """
        fx_rate = self.get_current_fx_rate(from_currency, to_currency)

        if fx_rate is None:
            return None

        return amount * fx_rate

    def convert_amount_historical_fx(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
        date: str,
    ) -> float | None:
        """
        Converts an amount using the FX rate around a historical purchase date.
        """
        fx_rate = self.get_historical_fx_rate(from_currency, to_currency, date)

        if fx_rate is None:
            return None

        return amount * fx_rate
    
    def get_asset_transaction_value_base(self, asset: Asset) -> float | None:
        """
        Returns the transaction value converted to the portfolio base currency
        using the historical FX rate around the purchase date.
        """
        asset_currency = self.get_asset_currency(asset.ticker)

        return self.convert_amount_historical_fx(
            asset.transaction_value,
            asset_currency,
            self.base_currency,
            asset.purchase_date,
        )

    def get_asset_current_value_base(self, asset: Asset) -> float | None:
        """
        Returns the current market value converted to the portfolio base currency
        using the latest FX rate.
        """
        current_price = self.get_current_price(asset.ticker)

        if current_price is None:
            return None

        asset_currency = self.get_asset_currency(asset.ticker)
        current_value_native = current_price * asset.quantity

        return self.convert_amount_current_fx(
            current_value_native,
            asset_currency,
            self.base_currency,
        )


        return self.convert_amount_historical_fx(
            asset.transaction_value,
            asset_currency,
            self.base_currency,
            asset.purchase_date,
        )

    def get_asset_current_value_base(self, asset: Asset) -> float | None:
        """
        Returns the current market value converted to the portfolio base currency
        using the latest FX rate.
        """
        current_price = self.get_current_price(asset.ticker)

        if current_price is None:
            return None

        asset_currency = self.get_asset_currency(asset.ticker)
        current_value_native = current_price * asset.quantity

        return self.convert_amount_current_fx(
            current_value_native,
            asset_currency,
            self.base_currency,
        )

    def total_transaction_value(self) -> float:
        """
        Returns the total invested amount in the portfolio base currency,
        using historical FX rates around the purchase dates.
        """
        total = 0.0

        for asset in self.assets:
            transaction_value = self.get_asset_transaction_value_base(asset)
            if transaction_value is not None:
                total += transaction_value

        return total

    def asset_weights_by_cost(self) -> list[dict]:
        """
        Returns the relative weight of each asset based on transaction value.
        Since current market prices are not included yet, this uses purchase values.
        """
        total_value = self.total_transaction_value()

        if total_value == 0:
            return []

        weights = []
        for asset in self.assets:
            weight = asset.transaction_value / total_value
            weights.append(
                {
                    "ticker": asset.ticker,
                    "weight": weight,
                    "transaction_value": asset.transaction_value,
                }
            )

        return weights

    def weights_by_sector(self) -> dict[str, float]:
        """
        Returns portfolio weights grouped by sector.
        """
        total_value = self.total_transaction_value()

        if total_value == 0:
            return {}

        sector_totals = {}
        for asset in self.assets:
            sector_totals[asset.sector] = sector_totals.get(asset.sector, 0) + asset.transaction_value

        return {
            sector: value / total_value
            for sector, value in sector_totals.items()
        }

    def weights_by_asset_class(self) -> dict[str, float]:
        """
        Returns portfolio weights grouped by asset class.
        """
        total_value = self.total_transaction_value()

        if total_value == 0:
            return {}

        class_totals = {}
        for asset in self.assets:
            class_totals[asset.asset_class] = class_totals.get(asset.asset_class, 0) + asset.transaction_value

        return {
            asset_class: value / total_value
            for asset_class, value in class_totals.items()
        }
    def get_current_price(self, ticker: str) -> float | None:
        """
        Fetches the latest closing price for a ticker using yfinance.
        """
        try:
            data = yf.Ticker(ticker).history(period="5d")
            if data.empty:
                return None
            return float(data["Close"].iloc[-1])
        except Exception:
            return None
        
    def get_asset_name(self, ticker: str) -> str:
        """
        Fetches the human-readable asset name for a ticker using yfinance.
        Falls back to the ticker if no name is available.
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info

            return (
                info.get("shortName")
                or info.get("longName")
                or ticker
            )
        except Exception:
            return ticker

    def get_historical_prices(self, ticker: str, period: str = "1y"):
        """
        Fetches historical price data for a ticker using yfinance.
        """
        try:
            data = yf.Ticker(ticker).history(period=period)
            return data
        except Exception:
            return None
        
    def get_asset_current_value(self, asset: Asset) -> float | None:
        """
        Returns the current market value of a single asset position.
        """
        current_price = self.get_current_price(asset.ticker)

        if current_price is None:
            return None

        return current_price * asset.quantity

    def total_current_value(self) -> float:
        """
        Returns the total current market value of the portfolio
        in the base currency.
        Assets for which no live price or FX rate is available are skipped.
        """
        total = 0.0

        for asset in self.assets:
            current_value = self.get_asset_current_value_base(asset)
            if current_value is not None:
                total += current_value

        return total

    def portfolio_snapshot(self) -> list[dict]:
        """
        Returns a snapshot of the portfolio including native and base-currency values.
        """
        snapshot = []
        total_current = self.total_current_value()

        for asset in self.assets:
            asset_currency = self.get_asset_currency(asset.ticker)
            current_price = self.get_current_price(asset.ticker)

            transaction_value_base = self.get_asset_transaction_value_base(asset)
            current_value_base = self.get_asset_current_value_base(asset)

            if current_value_base is not None and total_current > 0:
                asset_weight = current_value_base / total_current
            else:
                asset_weight = None

            snapshot.append(
                {
                    "ticker": asset.ticker,
                    "name": self.get_asset_name(asset.ticker),
                    "sector": asset.sector,
                    "asset_class": asset.asset_class,
                    "quantity": asset.quantity,
                    "purchase_price": asset.purchase_price,
                    "purchase_date": asset.purchase_date,
                    "asset_currency": asset_currency,
                    "transaction_value_native": asset.transaction_value,
                    "transaction_value_base": transaction_value_base,
                    "current_price": current_price,
                    "current_value_native": None if current_price is None else current_price * asset.quantity,
                    "current_value_base": current_value_base,
                    "asset_weight": asset_weight,
                }
            )

        return snapshot

    def asset_weights_by_current_value(self) -> list[dict]:
        """
        Returns the relative weight of each asset based on current market value
        in the portfolio base currency.
        """
        total_value = self.total_current_value()

        if total_value == 0:
            return []

        weights = []
        for asset in self.assets:
            current_value = self.get_asset_current_value_base(asset)

            if current_value is None:
                continue

            weight = current_value / total_value
            weights.append(
                {
                    "ticker": asset.ticker,
                    "current_value": current_value,
                    "weight": weight,
                }
            )

        return weights

    def current_weights_by_sector(self) -> dict[str, float]:
        """
        Returns portfolio weights grouped by sector based on current market value
        in the portfolio base currency.
        """
        total_value = self.total_current_value()

        if total_value == 0:
            return {}

        sector_totals = {}
        for asset in self.assets:
            current_value = self.get_asset_current_value_base(asset)

            if current_value is None:
                continue

            sector_totals[asset.sector] = sector_totals.get(asset.sector, 0) + current_value

        return {
            sector: value / total_value
            for sector, value in sector_totals.items()
        }

    def current_weights_by_asset_class(self) -> dict[str, float]:
        """
        Returns portfolio weights grouped by asset class based on current market value
        in the portfolio base currency.
        """
        class_totals = {}

        for asset in self.assets:
            current_value = self.get_asset_current_value_base(asset)

            if current_value is None:
                continue

            asset_class = asset.asset_class.strip().title()
            class_totals[asset_class] = class_totals.get(asset_class, 0.0) + current_value

        total_class_value = sum(class_totals.values())

        if total_class_value == 0:
            return {}

        return {
            asset_class: value / total_class_value
            for asset_class, value in class_totals.items()
        }
    
    def save_to_file(self, filepath: str) -> None:
        """
        Saves the portfolio assets to a JSON file.
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = [asdict(asset) for asset in self.assets]

        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def load_from_file(self, filepath: str) -> None:
        """
        Loads portfolio assets from a JSON file if it exists.
        """
        path = Path(filepath)

        if not path.exists():
            self.assets = []
            return

        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.assets = [Asset(**item) for item in data]

    def get_portfolio_weights_vector(self) -> tuple[list[str], np.ndarray]:
        """
        Returns portfolio tickers and their current-value weights as a numpy array.
        Only assets with available current values are included.
        """
        weights_data = self.asset_weights_by_current_value()

        if not weights_data:
            return [], np.array([])

        tickers = [item["ticker"] for item in weights_data]
        weights = np.array([item["weight"] for item in weights_data], dtype=float)

        return tickers, weights

    def get_historical_returns_matrix(self, period: str = "5y"):
        """
        Fetches historical closing prices for all portfolio tickers
        and returns a dataframe of monthly returns.
        """
        tickers, _ = self.get_portfolio_weights_vector()

        if not tickers:
            return None

        price_series = {}

        for ticker in tickers:
            data = self.get_historical_prices(ticker, period)

            if data is None or data.empty:
                continue

            if "Close" not in data.columns:
                continue

            monthly_prices = data["Close"].resample("ME").last().dropna()

            if len(monthly_prices) < 2:
                continue

            # Normalize all indices to the same month-end timestamp format
            monthly_prices.index = monthly_prices.index.tz_localize(None)
            monthly_prices.index = monthly_prices.index.to_period("M").to_timestamp("M")

            price_series[ticker] = monthly_prices

        if not price_series:
            return None

        prices_df = pd.concat(price_series, axis=1).sort_index()

        if prices_df.empty:
            return None

        returns_df = prices_df.pct_change(fill_method=None)

        # Keep rows where at least one ticker has a valid return
        returns_df = returns_df.dropna(how="all")

        if returns_df.empty:
            return None

        return returns_df

    def estimate_portfolio_parameters(self, period: str = "5y") -> tuple[float, float] | tuple[None, None]:
        """
        Estimates annualized portfolio drift and volatility from historical monthly returns.
        Handles missing ticker histories by reweighting available assets each month.
        """
        returns_df = self.get_historical_returns_matrix(period)
        tickers, weights = self.get_portfolio_weights_vector()

        if returns_df is None or returns_df.empty or len(weights) == 0:
            return None, None

        available_tickers = [ticker for ticker in tickers if ticker in returns_df.columns]

        if not available_tickers:
            return None, None

        filtered_weights = np.array(
            [weights[tickers.index(ticker)] for ticker in available_tickers],
            dtype=float,
        )

        if filtered_weights.sum() == 0:
            return None, None

        filtered_weights = filtered_weights / filtered_weights.sum()
        filtered_returns = returns_df[available_tickers]

        # Weighted returns with dynamic renormalization when some assets are missing
        weighted_returns = filtered_returns.fillna(0.0).mul(filtered_weights, axis=1).sum(axis=1)
        active_weights = filtered_returns.notna().mul(filtered_weights, axis=1).sum(axis=1)

        portfolio_monthly_returns = weighted_returns[active_weights > 0] / active_weights[active_weights > 0]
        portfolio_monthly_returns = portfolio_monthly_returns.dropna()

        if portfolio_monthly_returns.empty:
            return None, None

        mu_monthly = float(portfolio_monthly_returns.mean())
        sigma_monthly = float(portfolio_monthly_returns.std())

        mu_annual = mu_monthly * 12
        sigma_annual = sigma_monthly * np.sqrt(12)

        return mu_annual, sigma_annual

    def simulate_gbm_portfolio(
        self,
        years: int = 15,
        n_paths: int = 100_000,
        steps_per_year: int = 12,
        historical_period: str = "5y",
        confidence_level: float = 0.95,
    ) -> dict | None:
        """
        Simulates future portfolio values using a geometric Brownian motion model.
        """
        initial_value = self.total_current_value()

        if initial_value <= 0:
            return None

        mu, sigma = self.estimate_portfolio_parameters(historical_period)

        if mu is None or sigma is None:
            return None

        n_steps = years * steps_per_year
        dt = 1 / steps_per_year

        z = np.random.standard_normal((n_paths, n_steps))
        increments = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z
        log_paths = np.cumsum(increments, axis=1)

        paths = initial_value * np.exp(log_paths)
        paths = np.column_stack([np.full(n_paths, initial_value), paths])

        ending_values = paths[:, -1]

        mean_ending_value = float(np.mean(ending_values))
        median_ending_value = float(np.median(ending_values))
        percentile_5 = float(np.percentile(ending_values, 5))
        percentile_95 = float(np.percentile(ending_values, 95))

        var_threshold = float(np.percentile(ending_values, (1 - confidence_level) * 100))
        var_95 = max(0.0, initial_value - var_threshold)

        return {
            "initial_value": initial_value,
            "mu_annual": mu,
            "sigma_annual": sigma,
            "years": years,
            "n_paths": n_paths,
            "steps_per_year": steps_per_year,
            "mean_ending_value": mean_ending_value,
            "median_ending_value": median_ending_value,
            "percentile_5": percentile_5,
            "percentile_95": percentile_95,
            "var_95": var_95,
            "paths": paths,
        }