import pandas as pd
import numpy as np
from scipy.stats import zscore, norm

# Add standard indicators
def add_indicators(df):
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA10'] = df['Close'].rolling(window=10).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()

    df['BB_Middle'] = df['MA20']
    df['BB_Upper'] = df['MA20'] + 2 * df['Close'].rolling(window=20).std()
    df['BB_Lower'] = df['MA20'] - 2 * df['Close'].rolling(window=20).std()

    df['LogReturn'] = np.log(df['Close'] / df['Close'].shift(1))
    rolling_std = df['LogReturn'].rolling(window=20).std()
    df['HistVol'] = rolling_std * np.sqrt(252)

    df['ZScore'] = zscore(df['Close'].dropna())
    return df

# Calculate IV Rank

def calculate_iv_rank(current_iv, iv_series):
    iv_min = iv_series.min()
    iv_max = iv_series.max()
    if iv_max - iv_min == 0:
        return 0
    return (current_iv - iv_min) / (iv_max - iv_min)

# Calculate Moneyness

def calculate_moneyness(stock_price, strike_price):
    return (stock_price - strike_price) / stock_price

# Greeks using Black-Scholes

def black_scholes_delta(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    return norm.cdf(d1) if option_type == 'call' else norm.cdf(d1) - 1

def black_scholes_gamma(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    return norm.pdf(d1) / (S * sigma * np.sqrt(T))

def black_scholes_theta(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    pdf_d1 = norm.pdf(d1)
    if option_type == 'call':
        theta = - (S * pdf_d1 * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)
    else:
        theta = - (S * pdf_d1 * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)
    return theta / 365

# Full indicator augmentation

def add_all_indicators(df, option_row, risk_free_rate=0.01):
    df = add_indicators(df)

    iv_series = pd.Series([option_row['impliedVolatility']] * 100)
    current_iv = option_row['impliedVolatility']
    iv_rank = calculate_iv_rank(current_iv, iv_series)
    df['IV_Rank'] = iv_rank

    latest_price = df['Close'].iloc[-1]
    strike = option_row['strike']
    df['Moneyness'] = calculate_moneyness(latest_price, strike)

    today = pd.Timestamp.today()
    expiration = pd.to_datetime(option_row['expiration'])
    T = max((expiration - today).days / 365, 1e-6)

    sigma = current_iv
    S = latest_price
    K = strike
    r = risk_free_rate

    delta = black_scholes_delta(S, K, T, r, sigma)
    gamma = black_scholes_gamma(S, K, T, r, sigma)
    theta = black_scholes_theta(S, K, T, r, sigma)

    df['Delta'] = delta
    df['Gamma'] = gamma
    df['Theta'] = theta

    return df
