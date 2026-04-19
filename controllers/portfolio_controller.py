from models.asset import Asset
from models.portfolio import Portfolio
from views.chart_view import plot_price_history, plot_multiple_price_histories
from views.table_view import (
    display_assets,
    display_total_values,
    display_asset_weights,
    display_group_weights,
    display_price_history_table,
    display_calculation_breakdown,
)


class PortfolioController:
    """
    Controls the interaction between the portfolio model and the views.
    """

    def __init__(self):
        self.portfolio = Portfolio()
        self.filepath = "data/portfolio.json"
        self.portfolio.load_from_file(self.filepath)
        print(f"Loaded {len(self.portfolio.get_assets())} assets from file.")

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
        self.portfolio.save_to_file(self.filepath)

    def add_asset_interactive(self) -> None:
        """
        Prompts the user for asset details and adds the asset to the portfolio.
        """
        print("\nAdd a new asset")

        ticker = input("Ticker: ").strip().upper()
        sector = input("Sector: ").strip()
        asset_class = input("Asset class: ").strip()

        try:
            quantity = float(input("Quantity: ").strip())
            purchase_price = float(input("Purchase price: ").strip())
        except ValueError:
            print("Invalid input. Quantity and purchase price must be numbers.")
            return

        self.add_asset(ticker, sector, asset_class, quantity, purchase_price)
        print(f"Asset {ticker} added successfully.\n")

    def show_portfolio_summary(self) -> None:
        """
        Displays the current portfolio summary.
        """
        if not self.portfolio.get_assets():
            print("\nPortfolio is empty.\n")
            return

        snapshot = self.portfolio.portfolio_snapshot()

        display_assets(snapshot)
        display_total_values(
            self.portfolio.total_transaction_value(),
            self.portfolio.total_current_value(),
        )

    def run(self) -> None:
        """
        Runs the main CLI loop.
        """
        while True:
            print("\n=== Portfolio Tracker Menu ===")
            print("1. Add asset")
            print("2. View portfolio summary")
            print("3. Show current and historical price")
            print("4. Plot price graph")
            print("5. Show portfolio calculations")
            print("6. Exit")

            choice = input("Choose an option (1-6): ").strip()

            if choice == "1":
                self.add_asset_interactive()
            elif choice == "2":
                self.show_portfolio_summary()
            elif choice == "3":
                self.show_current_and_historical_price()
            elif choice == "4":
                self.plot_price_graph()
            elif choice == "5":
                self.show_portfolio_calculations()
            elif choice == "6":
                print("Exiting Portfolio Tracker. Goodbye.")
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.")
    
    def show_current_and_historical_price(self) -> None:
        """
        Prompts the user for a ticker and displays both current and historical price data.
        """
        ticker = input("Enter ticker: ").strip().upper()
        period = input("Enter period (e.g. 1mo, 6mo, 1y, 5y) [default=1mo]: ").strip()

        if not period:
            period = "1mo"

        current_price = self.portfolio.get_current_price(ticker)
        historical_data = self.portfolio.get_historical_prices(ticker, period)

        if current_price is None:
            print(f"Could not retrieve current price for {ticker}.")
        else:
            print(f"\nCurrent price of {ticker}: {current_price:.2f}\n")

        if historical_data is None or historical_data.empty:
            print(f"Could not retrieve historical data for {ticker}.")
            return

        display_price_history_table(ticker, historical_data)

    def plot_price_graph(self) -> None:
        """
        Prompts the user for one or more tickers and plots historical prices.
        Users can enter a single ticker or multiple tickers separated by commas.
        """
        ticker_input = input(
            "Enter ticker(s) separated by commas (e.g. AAPL or AAPL,MSFT,JNJ): "
        ).strip().upper()

        period = input("Enter period (e.g. 1mo, 6mo, 1y, 5y) [default=1y]: ").strip()

        if not period:
            period = "1y"

        tickers = [ticker.strip() for ticker in ticker_input.split(",") if ticker.strip()]

        if not tickers:
            print("No valid tickers entered.")
            return

        if len(tickers) == 1:
            ticker = tickers[0]
            data = self.portfolio.get_historical_prices(ticker, period)

            if data is None or data.empty:
                print(f"Could not retrieve historical data for {ticker}.")
                return

            plot_price_history(data, ticker)
            return

        price_data_dict = {}

        for ticker in tickers:
            data = self.portfolio.get_historical_prices(ticker, period)

            if data is None or data.empty:
                print(f"Warning: could not retrieve historical data for {ticker}.")
            else:
                price_data_dict[ticker] = data

        if not price_data_dict:
            print("Could not retrieve historical data for any of the selected tickers.")
            return

        plot_multiple_price_histories(price_data_dict)
    
    def show_portfolio_calculations(self) -> None:
        """
        Displays how total transaction value and total current value are obtained,
        along with the relative weights by sector and asset class.
        """
        if not self.portfolio.get_assets():
            print("\nPortfolio is empty.\n")
            return

        snapshot = self.portfolio.portfolio_snapshot()
        sector_weights = self.portfolio.current_weights_by_sector()
        asset_class_weights = self.portfolio.current_weights_by_asset_class()

        display_calculation_breakdown(snapshot)

        display_total_values(
            self.portfolio.total_transaction_value(),
            self.portfolio.total_current_value(),
        )

        if sector_weights:
            display_group_weights(
                "Weights by Sector (Current Value)",
                sector_weights,
            )
        else:
            print("No sector weights available.")

        if asset_class_weights:
            display_group_weights(
                "Weights by Asset Class (Current Value)",
                asset_class_weights,
            )
        else:
            print("No asset class weights available.")