from data_handler import fetch_data
from indicators import add_all_indicators
from strategy import recommend_trade
from visualize import plot_data
import yfinance as yf
import csv
from datetime import datetime
import os

def get_next_expiry(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    expirations = ticker.options
    return expirations[0]  # Get the nearest available expiration date

def log_trade(ticker, expiry, trade_signal):
    filename = "trade_log.csv"
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Date", "Ticker", "Expiry", "Trade Type", "Strike", "IV"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ticker,
            expiry,
            trade_signal.get("type", "N/A"),
            trade_signal.get("strike", "N/A"),
            trade_signal.get("iv", "N/A")
        ])

def main():
    ticker = input("Enter a stock ticker (e.g., AAPL): ").strip().upper()
    if not ticker:
        print("Invalid ticker input.")
        return

    print("Select timeframe:")
    print("1. 4 Hours")
    print("2. Weekly")
    print("3. Monthly")
    print("4. Yearly")

    choice = input("Enter option (1-4): ").strip()
    interval = "1d"
    period = "1y"

    if choice == "1":
        interval = "4h"
        period = "5d"
    elif choice == "2":
        interval = "1wk"
        period = "1y"
    elif choice == "3":
        interval = "1mo"
        period = "5y"
    elif choice == "4":
        interval = "1d"
        period = "1y"
    else:
        print("Invalid choice. Defaulting to daily/1y.")

    try:
        expiry = get_next_expiry(ticker)
        stock_data, options_data = fetch_data(ticker, expiry, interval=interval, period=period)

        option_row = {
            'strike': options_data.iloc[0]['strike'],
            'impliedVolatility': options_data.iloc[0]['impliedVolatility'],
            'expiration': expiry
        }

        enriched_data = add_all_indicators(stock_data, option_row)
        trade_signal = recommend_trade(enriched_data, options_data, expiry)
        print("Trade Recommendation:", trade_signal)

        log_trade(ticker, expiry, trade_signal)
        plot_data(enriched_data)

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")

if __name__ == "__main__":
    main()
