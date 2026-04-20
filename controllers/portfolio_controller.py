from models.asset import Asset
from models.portfolio import Portfolio
from views.chart_view import (
    plot_multiple_price_histories,
    plot_normalized_price_histories,
    plot_price_history,
    plot_simulation_histogram,
    plot_simulation_paths,
)
from views.table_view import (
    display_additional_metrics,
    display_assets,
    display_calculation_breakdown,
    display_group_weights,
    display_price_history_table,
    display_simulation_results,
    display_total_values,
)


class PortfolioController:
    """
    Controls the interaction between the portfolio model and the views.
    """

    def __init__(self):
        self.portfolio = Portfolio()
        self.filepath = "data/portfolio.json"
        self.portfolio.load_from_file(self.filepath)

    # ------------------------------------------------------------------
    # Asset creation
    # ------------------------------------------------------------------
    def add_asset(
        self,
        ticker: str,
        sector: str,
        asset_class: str,
        quantity: float,
        purchase_price: float,
        purchase_date: str,
    ) -> None:
        """
        Creates an Asset and adds it to the portfolio.
        """
        asset = Asset(ticker, sector, asset_class, quantity, purchase_price, purchase_date)
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

        purchase_date = input("Purchase date (YYYY-MM-DD): ").strip()

        self.add_asset(ticker, sector, asset_class, quantity, purchase_price, purchase_date)
        print(f"Asset {ticker} added successfully.\n")
    
    def delete_asset_interactive(self) -> None:
        """
        Displays all assets and lets the user delete one by index.
        """
        assets = self.portfolio.get_assets()

        if not assets:
            print("\nPortfolio is empty.\n")
            return

        print("\nCurrent portfolio assets:")
        for i, asset in enumerate(assets, start=1):
            print(
                f"{i}. {asset.ticker} | {asset.sector} | {asset.asset_class} | "
                f"Qty: {asset.quantity} | Purchase Price: {asset.purchase_price}"
            )

        choice = input("\nEnter the number of the asset to delete: ").strip()

        try:
            asset_index = int(choice) - 1
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

        if self.portfolio.remove_asset_by_index(asset_index):
            self.portfolio.save_to_file(self.filepath)
            print("Asset deleted successfully.\n")
        else:
            print("Invalid selection. No asset was deleted.\n")
        
    def change_base_currency_interactive(self) -> None:
        """
        Prompts the user to change the portfolio base currency.
        """
        print(f"\nCurrent base currency: {self.portfolio.base_currency}")
        new_currency = input("Enter new base currency (e.g. USD, EUR): ").strip().upper()

        if not new_currency:
            print("No currency entered. Base currency unchanged.\n")
            return

        self.portfolio.set_base_currency(new_currency)
        print(f"Base currency changed to {self.portfolio.base_currency}.\n")

    # ------------------------------------------------------------------
    # Portfolio views
    # ------------------------------------------------------------------
    def show_portfolio_summary(self) -> None:
        """
        Displays the current portfolio summary.
        """
        if not self.portfolio.get_assets():
            print("\nPortfolio is empty.\n")
            return

        snapshot = self.portfolio.portfolio_snapshot()

        display_assets(snapshot, self.portfolio.base_currency)
        display_total_values(
            self.portfolio.total_transaction_value(),
            self.portfolio.total_current_value(),
            self.portfolio.base_currency,
        )

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
        sharpe_ratio = self.portfolio.calculate_sharpe_ratio()
        max_drawdown = self.portfolio.calculate_max_drawdown()

        display_calculation_breakdown(snapshot, self.portfolio.base_currency)

        display_total_values(
            self.portfolio.total_transaction_value(),
            self.portfolio.total_current_value(),
            self.portfolio.base_currency,
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

        display_additional_metrics(sharpe_ratio, max_drawdown)

    # ------------------------------------------------------------------
    # Price lookup and charting
    # ------------------------------------------------------------------
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
        Prompts the user for one or more tickers and plots either raw prices
        or normalized performance.
        """
        ticker_input = input(
            "Enter ticker(s) separated by commas (e.g. AAPL or AAPL,MSFT,JNJ): "
        ).strip().upper()

        period = input("Enter period (e.g. 1mo, 6mo, 1y, 5y) [default=1y]: ").strip()

        if not period:
            period = "1y"

        print("\nChoose graph type:")
        print("1. Raw price graph")
        print("2. Normalized performance graph")

        graph_choice = input("Choose an option (1-2): ").strip()

        tickers = [ticker.strip() for ticker in ticker_input.split(",") if ticker.strip()]

        if not tickers:
            print("No valid tickers entered.")
            return

        if graph_choice == "1":
            if len(tickers) == 1:
                ticker = tickers[0]
                data = self.portfolio.get_historical_prices(ticker, period)

                if data is None or data.empty:
                    print(f"Could not retrieve historical data for {ticker}.")
                    return

                currency = self.portfolio.get_asset_currency(ticker)
                plot_price_history(data, ticker, currency)
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

        elif graph_choice == "2":
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

            plot_normalized_price_histories(price_data_dict)

        else:
            print("Invalid graph type choice.")

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------
    def run_portfolio_simulation(self) -> None:
        """
        Runs a 15-year portfolio simulation and lets the user choose the model.
        """
        if not self.portfolio.get_assets():
            print("\nPortfolio is empty.\n")
            return

        print("\nChoose simulation model:")
        print("1. Portfolio-level GBM")
        print("2. Correlated multi-asset simulation")

        model_choice = input("Choose an option (1-2): ").strip()

        print("\nRunning 15-year portfolio simulation with 100,000 paths...")

        if model_choice == "1":
            results = self.portfolio.simulate_gbm_portfolio(
                years=15,
                n_paths=100_000,
                steps_per_year=12,
                historical_period="5y",
                confidence_level=0.95,
            )
        elif model_choice == "2":
            results = self.portfolio.simulate_correlated_portfolio(
                years=15,
                n_paths=100_000,
                steps_per_year=12,
                historical_period="5y",
                confidence_level=0.95,
            )
        else:
            print("Invalid simulation model choice.")
            return

        if results is None:
            print("Simulation could not be run. Check whether sufficient price data is available.")
            return

        display_simulation_results(results, self.portfolio.base_currency)

        if "paths" in results:
            paths_to_plot = results["paths"]
        else:
            paths_to_plot = results["portfolio_paths"]

        plot_simulation_paths(
            paths_to_plot,
            results["years"],
            self.portfolio.base_currency,
            model_name=results.get("model", "Portfolio Simulation"),
            max_paths_to_plot=100,
        )

        plot_simulation_histogram(
            paths_to_plot[:, -1],
            self.portfolio.base_currency,
            model_name=results.get("model", "Portfolio Simulation"),
            bins=50,
        )

    # ------------------------------------------------------------------
    # Main CLI loop
    # ------------------------------------------------------------------
    def run(self) -> None:
        """
        Runs the main CLI loop.
        """
        while True:
            print("1. Add asset")
            print("2. Delete asset")
            print("3. Change base currency")
            print("4. View portfolio summary")
            print("5. Show current and historical price")
            print("6. Plot price graph")
            print("7. Show portfolio calculations")
            print("8. Run 15-year portfolio simulation")
            print("9. Exit")

            choice = input("Choose an option (1-9): ").strip()

            if choice == "1":
                self.add_asset_interactive()
            elif choice == "2":
                self.delete_asset_interactive()
            elif choice == "3":
                self.change_base_currency_interactive()
            elif choice == "4":
                self.show_portfolio_summary()
            elif choice == "5":
                self.show_current_and_historical_price()
            elif choice == "6":
                self.plot_price_graph()
            elif choice == "7":
                self.show_portfolio_calculations()
            elif choice == "8":
                self.run_portfolio_simulation()
            elif choice == "9":
                print("Exiting Portfolio Tracker. Goodbye.")
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, 7, 8, or 9.")