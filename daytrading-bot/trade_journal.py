import pandas as pd

def load_trade_log(filename="trade_log.csv"):
    try:
        df = pd.read_csv(filename, parse_dates=["Date"])
        return df
    except FileNotFoundError:
        print("Trade log not found.")
        return pd.DataFrame()

def display_trades(df):
    print("\nFull Trade Log:")
    print(df.to_string(index=False))

def filter_trades(df):
    ticker = input("Filter by ticker (or press Enter to skip): ").strip().upper()
    trade_type = input("Filter by trade type (Call/Put or Enter to skip): ").strip().capitalize()
    start_date = input("Start date (YYYY-MM-DD or Enter to skip): ").strip()
    end_date = input("End date (YYYY-MM-DD or Enter to skip): ").strip()

    if ticker:
        df = df[df["Ticker"] == ticker]
    if trade_type in ["Call", "Put"]:
        df = df[df["Trade Type"] == trade_type]
    if start_date:
        df = df[df["Date"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["Date"] <= pd.to_datetime(end_date)]

    print("\nFiltered Trade Log:")
    print(df.to_string(index=False))

def main():
    df = load_trade_log()
    if df.empty:
        return

    display_trades(df)
    print("\n--- Apply Filters ---")
    filter_trades(df)

if __name__ == "__main__":
    main()
