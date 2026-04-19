from rich.console import Console
from rich.table import Table


console = Console()


def display_assets(assets: list[dict]) -> None:
    """
    Displays all assets in a formatted table.
    """
    table = Table(title="Portfolio Assets")

    table.add_column("Ticker", justify="left")
    table.add_column("Name", justify="left")
    table.add_column("Sector", justify="left")
    table.add_column("Asset Class", justify="left")
    table.add_column("Quantity", justify="right")
    table.add_column("Purchase Price", justify="right")
    table.add_column("Transaction Value", justify="right")
    table.add_column("Current Price", justify="right")
    table.add_column("Current Value", justify="right")

    for asset in assets:
        current_price = (
            f"{asset['current_price']:.2f}"
            if asset["current_price"] is not None
            else "N/A"
        )
        current_value = (
            f"{asset['current_value']:.2f}"
            if asset["current_value"] is not None
            else "N/A"
        )

        table.add_row(
            asset["ticker"],
            asset["name"],
            asset["sector"],
            asset["asset_class"],
            f"{asset['quantity']:.2f}",
            f"{asset['purchase_price']:.2f}",
            f"{asset['transaction_value']:.2f}",
            current_price,
            current_value,
        )

    console.print(table)

def display_total_values(transaction_value: float, current_value: float) -> None:
    """
    Displays both total transaction value and total current market value.
    """
    console.print(f"\n[bold green]Total Transaction Value:[/bold green] {transaction_value:.2f}")
    console.print(f"[bold cyan]Total Current Value:[/bold cyan] {current_value:.2f}")

def display_asset_weights(weights: list[dict]) -> None:
    """
    Displays asset weights in a formatted table.
    """
    table = Table(title="Asset Weights by Current Value")

    table.add_column("Ticker", justify="left")
    table.add_column("Current Value", justify="right")
    table.add_column("Weight", justify="right")

    for item in weights:
        table.add_row(
            item["ticker"],
            f"{item['current_value']:.2f}",
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

def display_price_history_table(ticker: str, price_data, rows: int = 10) -> None:
    """
    Displays recent historical closing prices for a ticker in a table.
    """
    if price_data is None or price_data.empty:
        console.print(f"[bold red]No historical data available for {ticker}.[/bold red]")
        return

    table = Table(title=f"{ticker} Historical Prices")

    table.add_column("Date", justify="left")
    table.add_column("Open", justify="right")
    table.add_column("High", justify="right")
    table.add_column("Low", justify="right")
    table.add_column("Close", justify="right")
    table.add_column("Volume", justify="right")

    recent_data = price_data.tail(rows)

    for date, row in recent_data.iterrows():
        table.add_row(
            str(date.date()),
            f"{row['Open']:.2f}",
            f"{row['High']:.2f}",
            f"{row['Low']:.2f}",
            f"{row['Close']:.2f}",
            f"{int(row['Volume'])}",
        )

    console.print(table)

def display_calculation_breakdown(assets: list[dict]) -> None:
    """
    Displays the per-asset calculation breakdown used to obtain
    total transaction value and total current value.
    """
    table = Table(title="Portfolio Calculation Breakdown")

    table.add_column("Ticker", justify="left")
    table.add_column("Name", justify="left")
    table.add_column("Quantity", justify="right")
    table.add_column("Purchase Price", justify="right")
    table.add_column("Transaction Value", justify="right")
    table.add_column("Current Price", justify="right")
    table.add_column("Current Value", justify="right")
    table.add_column("Asset Weight (Current Value)", justify="right")

    for asset in assets:
        current_price = (
            f"{asset['current_price']:.2f}"
            if asset["current_price"] is not None
            else "N/A"
        )
        current_value = (
            f"{asset['current_value']:.2f}"
            if asset["current_value"] is not None
            else "N/A"
        )
        asset_weight = (
            f"{asset['asset_weight']:.2%}"
            if asset["asset_weight"] is not None
            else "N/A"
        )

        table.add_row(
            asset["ticker"],
            asset["name"],
            f"{asset['quantity']:.2f}",
            f"{asset['purchase_price']:.2f}",
            f"{asset['transaction_value']:.2f}",
            current_price,
            current_value,
            asset_weight,
        )

    console.print(table)