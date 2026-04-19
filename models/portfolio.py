from models.asset import Asset
import yfinance as yf
import json
from dataclasses import asdict
from pathlib import Path


class Portfolio:
    """
    Represents an investment portfolio containing multiple assets.
    Handles storage and basic portfolio calculations.
    """

    def __init__(self):
        self.assets = []

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

    def total_transaction_value(self) -> float:
        """
        Returns the total invested amount based on purchase prices.
        """
        return sum(asset.transaction_value for asset in self.assets)

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
        Returns the total current market value of the portfolio.
        Assets for which no live price is available are skipped.
        """
        total = 0.0

        for asset in self.assets:
            current_value = self.get_asset_current_value(asset)
            if current_value is not None:
                total += current_value

        return total

    def portfolio_snapshot(self) -> list[dict]:
        """
        Returns a snapshot of the portfolio including purchase values,
        current values, and relative asset weights.
        """
        snapshot = []
        total_current = self.total_current_value()

        for asset in self.assets:
            current_price = self.get_current_price(asset.ticker)
            current_value = None if current_price is None else current_price * asset.quantity

            if current_value is not None and total_current > 0:
                asset_weight = current_value / total_current
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
                    "transaction_value": asset.transaction_value,
                    "current_price": current_price,
                    "current_value": current_value,
                    "asset_weight": asset_weight,
                }
            )

        return snapshot

    def asset_weights_by_current_value(self) -> list[dict]:
        """
        Returns the relative weight of each asset based on current market value.
        Assets with unavailable prices are skipped.
        """
        total_value = self.total_current_value()

        if total_value == 0:
            return []

        weights = []
        for asset in self.assets:
            current_value = self.get_asset_current_value(asset)

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
        Returns portfolio weights grouped by sector based on current market value.
        """
        total_value = self.total_current_value()

        if total_value == 0:
            return {}

        sector_totals = {}
        for asset in self.assets:
            current_value = self.get_asset_current_value(asset)

            if current_value is None:
                continue

            sector_totals[asset.sector] = sector_totals.get(asset.sector, 0) + current_value

        return {
            sector: value / total_value
            for sector, value in sector_totals.items()
        }

    def current_weights_by_asset_class(self) -> dict[str, float]:
        """
        Returns portfolio weights grouped by asset class based on current market value.
        """
        total_value = self.total_current_value()

        if total_value == 0:
            return {}

        class_totals = {}
        for asset in self.assets:
            current_value = self.get_asset_current_value(asset)

            if current_value is None:
                continue

            class_totals[asset.asset_class] = class_totals.get(asset.asset_class, 0) + current_value

        return {
            asset_class: value / total_value
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