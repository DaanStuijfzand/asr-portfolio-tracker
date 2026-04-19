from rich.console import Console
from rich.table import Table


console = Console()


def display_assets(assets: list) -> None:
    """
    Displays all assets in a formatted table.
    """
    table = Table(title="Portfolio Assets")

    table.add_column("Ticker", justify="left")
    table.add_column("Sector", justify="left")
    table.add_column("Asset Class", justify="left")
    table.add_column("Quantity", justify="right")
    table.add_column("Purchase Price", justify="right")
    table.add_column("Transaction Value", justify="right")

    for asset in assets:
        table.add_row(
            asset.ticker,
            asset.sector,
            asset.asset_class,
            f"{asset.quantity:.2f}",
            f"{asset.purchase_price:.2f}",
            f"{asset.transaction_value:.2f}",
        )

    console.print(table)


def display_total_value(total_value: float) -> None:
    """
    Displays the total portfolio transaction value.
    """
    console.print(f"\n[bold green]Total Transaction Value:[/bold green] {total_value:.2f}")


def display_asset_weights(weights: list[dict]) -> None:
    """
    Displays asset weights in a formatted table.
    """
    table = Table(title="Asset Weights by Cost")

    table.add_column("Ticker", justify="left")
    table.add_column("Transaction Value", justify="right")
    table.add_column("Weight", justify="right")

    for item in weights:
        table.add_row(
            item["ticker"],
            f"{item['transaction_value']:.2f}",
            f"{item['weight']:.2%}",
        )

    console.print(table)


def display_group_weights(title: str, weights: dict[str, float]) -> None:
    """
    Displays grouped portfolio weights such as by sector or asset class.
    """
    table = Table(title=title)

    table.add_column("Category", justify="left")
    table.add_column("Weight", justify="right")

    for category, weight in weights.items():
        table.add_row(category, f"{weight:.2%}")

    console.print(table)