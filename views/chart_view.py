import matplotlib.pyplot as plt


def plot_price_history(price_data, ticker: str) -> None:
    """
    Plots historical closing prices for a given ticker.
    """
    if price_data.empty:
        print(f"No historical data available for {ticker}.")
        return

    plt.figure(figsize=(10, 5))
    plt.plot(price_data.index, price_data["Close"])
    plt.title(f"{ticker} Historical Closing Prices")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True)
    plt.tight_layout()
    plt.show()