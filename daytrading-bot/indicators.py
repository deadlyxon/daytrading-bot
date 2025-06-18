import pandas as pd
import numpy as np

def calculate_moving_average(df, period=20):
    return df['Close'].rolling(window=period).mean()

def calculate_z_score(df, period=20):
    rolling_mean = df['Close'].rolling(window=period).mean()
    rolling_std = df['Close'].rolling(window=period).std()
    return (df['Close'] - rolling_mean) / rolling_std

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(series, short=12, long=26, signal=9):
    ema_short = series.ewm(span=short, adjust=False).mean()
    ema_long = series.ewm(span=long, adjust=False).mean()
    macd = ema_short - ema_long
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def calculate_moneyness(spot_price, strike_price):
    return (spot_price - strike_price) / spot_price

def calculate_iv_rank(current_iv, iv_series):
    return (iv_series < current_iv).mean()

def black_scholes_delta(S, K, T, r, sigma, call=True):
    from scipy.stats import norm
    from numpy import log, sqrt, exp
    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    return norm.cdf(d1) if call else -norm.cdf(-d1)

def black_scholes_gamma(S, K, T, r, sigma):
    from scipy.stats import norm
    from numpy import log, sqrt, exp
    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    return norm.pdf(d1) / (S * sigma * np.sqrt(T))

def black_scholes_theta(S, K, T, r, sigma, call=True):
    from scipy.stats import norm
    from numpy import log, sqrt, exp
    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    first_term = - (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
    if call:
        second_term = r * K * exp(-r * T) * norm.cdf(d2)
        return first_term - second_term
    else:
        second_term = r * K * exp(-r * T) * norm.cdf(-d2)
        return first_term + second_term

def add_all_indicators(df, option_row):
    df = df.copy()
    df['MA20'] = calculate_moving_average(df, 20)
    df['ZScore'] = calculate_z_score(df, 20)
    return df
