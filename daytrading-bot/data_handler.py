import yfinance as yf
import pandas as pd

def fetch_data(ticker, expiry, interval="4h", period="7d"):
    stock = yf.Ticker(ticker)
    stock_hist = stock.history(period=period, interval=interval)

    try:
        options_chain = stock.option_chain(expiry)
        calls = options_chain.calls
        puts = options_chain.puts
        return stock_hist, calls, puts
    except Exception:
        return stock_hist, pd.DataFrame(), pd.DataFrame()
