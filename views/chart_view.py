import matplotlib.pyplot as plt
import numpy as np


# ------------------------------------------------------------------
# Price chart views
# ------------------------------------------------------------------
def plot_price_history(price_data, ticker: str, currency: str) -> None:
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
    plt.ylabel(f"Price ({currency})")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_multiple_price_histories(price_series_dict: dict[str, object]) -> None:
    """
    Plots historical closing prices for multiple tickers on one graph.
    Prices are shown in each asset's native currency.
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
    plt.ylabel("Price (Native Asset Currency)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


# ------------------------------------------------------------------
# Simulation chart views
# ------------------------------------------------------------------
def plot_simulation_paths(
    paths: np.ndarray,
    years: int,
    base_currency: str,
    model_name: str = "Portfolio Simulation",
    max_paths_to_plot: int = 100,
) -> None:
    """
    Plots a subset of simulated portfolio paths in the portfolio base currency.
    """
    if paths is None or len(paths) == 0:
        print("No simulation paths available to plot.")
        return

    n_paths, n_points = paths.shape
    paths_to_plot = min(max_paths_to_plot, n_paths)

    time_axis = np.linspace(0, years, n_points)

    plt.figure(figsize=(10, 5))

    for i in range(paths_to_plot):
        plt.plot(time_axis, paths[i], alpha=0.4)

    plt.title(f"{model_name} ({paths_to_plot} of {n_paths} paths shown)")
    plt.xlabel("Years")
    plt.ylabel(f"Portfolio Value ({base_currency})")
    plt.grid(True)
    plt.tight_layout()
    plt.show()