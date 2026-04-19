import matplotlib.pyplot as plt


def plot_price_history(price_data, ticker: str) -> None:
    """
    Plots historical closing prices for a single ticker.
    """
    if price_data is None or price_data.empty:
        print(f"No historical data available for {ticker}.")
        return

    plt.figure(figsize=(10, 5))
    plt.plot(price_data.index, price_data["Close"], label=ticker)
    plt.title(f"{ticker} Historical Closing Prices")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_multiple_price_histories(price_series_dict: dict[str, object]) -> None:
    """
    Plots historical closing prices for multiple tickers on one graph.
    """
    if not price_series_dict:
        print("No price data available to plot.")
        return

    plt.figure(figsize=(10, 5))

    plotted_any = False

    for ticker, price_data in price_series_dict.items():
        if price_data is None or price_data.empty:
            continue

        plt.plot(price_data.index, price_data["Close"], label=ticker)
        plotted_any = True

    if not plotted_any:
        print("No valid historical data available for the selected tickers.")
        return

    plt.title("Historical Closing Prices")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()