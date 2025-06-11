import yfinance as yf
import pandas as pd

def fetch_data(ticker, expiry, interval="1d", period="1y"):
    stock = yf.Ticker(ticker)
    stock_hist = stock.history(period=period, interval=interval)
    options_chain = stock.option_chain(expiry)
    return stock_hist, options_chain.calls
