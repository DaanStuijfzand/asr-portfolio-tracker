from models.asset import Asset
from models.portfolio import Portfolio
from views.table_view import (
    display_assets,
    display_total_value,
    display_asset_weights,
    display_group_weights,
)


class PortfolioController:
    """
    Controls the interaction between the portfolio model and the views.
    """

    def __init__(self):
        self.portfolio = Portfolio()

    def add_asset(
        self,
        ticker: str,
        sector: str,
        asset_class: str,
        quantity: float,
        purchase_price: float,
    ) -> None:
        """
        Creates an Asset and adds it to the portfolio.
        """
        asset = Asset(ticker, sector, asset_class, quantity, purchase_price)
        self.portfolio.add_asset(asset)

    def show_portfolio_summary(self) -> None:
        """
        Displays the current portfolio summary.
        """
        display_assets(self.portfolio.get_assets())
        display_total_value(self.portfolio.total_transaction_value())
        display_asset_weights(self.portfolio.asset_weights_by_cost())
        display_group_weights("Weights by Sector", self.portfolio.weights_by_sector())
        display_group_weights("Weights by Asset Class", self.portfolio.weights_by_asset_class())