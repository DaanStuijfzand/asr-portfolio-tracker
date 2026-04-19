from models.asset import Asset


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