from rich.console import Console
from rich.table import Table


console = Console()


def display_assets(assets: list[dict], base_currency: str) -> None:
    """
    Displays all assets in a formatted portfolio summary table.
    """
    table = Table(title=f"Portfolio Assets (Base Currency: {base_currency})")

    table.add_column("Ticker", justify="left")
    table.add_column("Name", justify="left")
    table.add_column("Asset Currency", justify="left")
    table.add_column("Sector", justify="left")
    table.add_column("Asset Class", justify="left")
    table.add_column("Quantity", justify="right")
    table.add_column("Purchase Price (Asset Currency)", justify="right")
    table.add_column(f"Transaction Value ({base_currency})", justify="right")
    table.add_column("Current Price (Asset Currency)", justify="right")
    table.add_column(f"Current Value ({base_currency})", justify="right")

    for asset in assets:
        transaction_value_base = (
            f"{asset['transaction_value_base']:.2f}"
            if asset["transaction_value_base"] is not None
            else "N/A"
        )
        current_price = (
            f"{asset['current_price']:.2f}"
            if asset["current_price"] is not None
            else "N/A"
        )
        current_value_base = (
            f"{asset['current_value_base']:.2f}"
            if asset["current_value_base"] is not None
            else "N/A"
        )

        table.add_row(
            asset["ticker"],
            asset["name"],
            asset["asset_currency"],
            asset["sector"],
            asset["asset_class"],
            f"{asset['quantity']:.2f}",
            f"{asset['purchase_price']:.2f}",
            transaction_value_base,
            current_price,
            current_value_base,
        )

    console.print(table)

def display_total_values(transaction_value: float, current_value: float, base_currency: str) -> None:
    """
    Displays both total transaction value and total current market value
    in the portfolio base currency.
    """
    console.print(
        f"\n[bold green]Total Transaction Value ({base_currency}):[/bold green] {transaction_value:.2f}"
    )
    console.print(
        f"[bold cyan]Total Current Value ({base_currency}):[/bold cyan] {current_value:.2f}"
    )

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

def display_price_history_table(ticker: str, price_data, rows: int = 30) -> None:
    """
    Displays recent historical closing prices for a ticker in a table,
    together with the available historical date range.
    """
    if price_data is None or price_data.empty:
        console.print(f"[bold red]No historical data available for {ticker}.[/bold red]")
        return

    start_date = str(price_data.index.min().date())
    end_date = str(price_data.index.max().date())

    console.print(
        f"\n[bold cyan]Available historical data for {ticker}:[/bold cyan] {start_date} to {end_date}\n"
    )

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

def display_calculation_breakdown(assets: list[dict], base_currency: str) -> None:
    """
    Displays the per-asset calculation breakdown used to obtain
    total transaction value and total current value.
    """
    table = Table(title=f"Portfolio Calculation Breakdown (Base Currency: {base_currency})")

    table.add_column("Ticker", justify="left")
    table.add_column("Name", justify="left")
    table.add_column("Asset Currency", justify="left")
    table.add_column("Quantity", justify="right")
    table.add_column("Purchase Price (Asset Currency)", justify="right")
    table.add_column(f"Transaction Value ({base_currency})", justify="right")
    table.add_column("Current Price (Asset Currency)", justify="right")
    table.add_column(f"Current Value ({base_currency})", justify="right")
    table.add_column("Asset Weight", justify="right")

    for asset in assets:
        transaction_value_base = (
            f"{asset['transaction_value_base']:.2f}"
            if asset["transaction_value_base"] is not None
            else "N/A"
        )
        current_price = (
            f"{asset['current_price']:.2f}"
            if asset["current_price"] is not None
            else "N/A"
        )
        current_value_base = (
            f"{asset['current_value_base']:.2f}"
            if asset["current_value_base"] is not None
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
            asset["asset_currency"],
            f"{asset['quantity']:.2f}",
            f"{asset['purchase_price']:.2f}",
            transaction_value_base,
            current_price,
            current_value_base,
            asset_weight,
        )

    console.print(table)

def display_simulation_results(results: dict, base_currency: str) -> None:
    """
    Displays a summary of portfolio simulation results.
    """
    table = Table(title=f"Portfolio Simulation Results (Base Currency: {base_currency})")

    table.add_column("Metric", justify="left")
    table.add_column("Value", justify="right")

    table.add_row("Initial Portfolio Value", f"{results['initial_value']:.2f} {base_currency}")
    table.add_row("Estimated Annual Return (mu)", f"{results['mu_annual']:.2%}")
    table.add_row("Estimated Annual Volatility (sigma)", f"{results['sigma_annual']:.2%}")
    table.add_row("Simulation Horizon (Years)", f"{results['years']}")
    table.add_row("Number of Paths", f"{results['n_paths']:,}")
    table.add_row("Expected Ending Value", f"{results['mean_ending_value']:.2f} {base_currency}")
    table.add_row("Median Ending Value", f"{results['median_ending_value']:.2f} {base_currency}")
    table.add_row("5th Percentile Ending Value", f"{results['percentile_5']:.2f} {base_currency}")
    table.add_row("95th Percentile Ending Value", f"{results['percentile_95']:.2f} {base_currency}")
    table.add_row("VaR (95%)", f"{results['var_95']:.2f} {base_currency}")

    console.print(table)

def display_additional_metrics(sharpe_ratio: float | None, max_drawdown: float | None) -> None:
    """
    Displays additional portfolio risk and performance metrics.
    """
    table = Table(title="Additional Portfolio Metrics")

    table.add_column("Metric", justify="left")
    table.add_column("Value", justify="right")

    sharpe_display = f"{sharpe_ratio:.4f}" if sharpe_ratio is not None else "N/A"
    max_drawdown_display = f"{max_drawdown:.2%}" if max_drawdown is not None else "N/A"

    table.add_row("Sharpe Ratio", sharpe_display)
    table.add_row("Maximum Drawdown", max_drawdown_display)

    console.print(table)