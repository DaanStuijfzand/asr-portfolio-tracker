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

    @property
    def transaction_value(self) -> float:
        """
        Returns the original transaction value of the asset.
        """
        return self.quantity * self.purchase_price