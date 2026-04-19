from controllers.portfolio_controller import PortfolioController


def main():
    controller = PortfolioController()

    controller.add_asset("AAPL", "Technology", "Equity", 10, 150.0)
    controller.add_asset("MSFT", "Technology", "Equity", 5, 200.0)
    controller.add_asset("JNJ", "Healthcare", "Equity", 8, 100.0)

    controller.show_portfolio_summary()


if __name__ == "__main__":
    main()