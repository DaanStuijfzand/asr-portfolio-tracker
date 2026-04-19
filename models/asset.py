from dataclasses import dataclass


@dataclass
class Asset:
    """
    Represents a single asset position in the portfolio.
    """

    ticker: str
    sector: str
    asset_class: str
    quantity: float
    purchase_price: float
    purchase_date: str

    @property
    def transaction_value(self) -> float:
        """
        Returns the original transaction value of the asset
        in the asset's native currency.
        """
        return self.quantity * self.purchase_price