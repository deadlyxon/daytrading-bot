from indicators import (
    calculate_moneyness,
    calculate_iv_rank,
    black_scholes_delta,
    black_scholes_gamma,
    black_scholes_theta
)
import pandas as pd
import numpy as np

def recommend_trade(stock_df, options_df, expiry, risk_free_rate=0.01):
    latest_price = stock_df['Close'].iloc[-1]
    today = pd.Timestamp.today()
    expiration = pd.to_datetime(expiry)
    T = max((expiration - today).days / 365, 1e-6)

    options_df = options_df.copy()

    options_df['Moneyness'] = options_df['strike'].apply(
        lambda strike: calculate_moneyness(latest_price, strike)
    )
    options_df['Delta'] = options_df.apply(
        lambda row: black_scholes_delta(
            S=latest_price,
            K=row['strike'],
            T=T,
            r=risk_free_rate,
            sigma=row['impliedVolatility']
        ), axis=1
    )
    options_df['Gamma'] = options_df.apply(
        lambda row: black_scholes_gamma(
            S=latest_price,
            K=row['strike'],
            T=T,
            r=risk_free_rate,
            sigma=row['impliedVolatility']
        ), axis=1
    )
    options_df['Theta'] = options_df.apply(
        lambda row: black_scholes_theta(
            S=latest_price,
            K=row['strike'],
            T=T,
            r=risk_free_rate,
            sigma=row['impliedVolatility']
        ), axis=1
    )

    iv_series = options_df['impliedVolatility']
    options_df['IV_Rank'] = iv_series.apply(
        lambda iv: calculate_iv_rank(iv, iv_series)
    )

    # FILTERS
    options_df = options_df[options_df['inTheMoney'] == False]
    options_df = options_df[options_df['volume'] > 500]
    options_df = options_df[options_df['openInterest'] > 500]
    options_df = options_df[options_df['IV_Rank'] <= 0.75]
    options_df = options_df[(options_df['Delta'].abs() >= 0.25) & (options_df['Delta'].abs() <= 0.7)]
    options_df = options_df[options_df['Moneyness'].abs() <= 0.10]
    options_df = options_df[(options_df['ask'] - options_df['bid']) / options_df['ask'] <= 0.2]

    if options_df.empty:
        return "No valid options found"

    z_score = stock_df['ZScore'].iloc[-1]

    if z_score > 1:
        trade_type = 'Call'
    elif z_score < -1:
        trade_type = 'Put'
    else:
        return "No strong signal"

    top_options = options_df.sort_values(by='IV_Rank').head(3).copy()

    if top_options.empty:
        return "No valid options found"

    top_options['type'] = trade_type
    return top_options.to_dict(orient='records')
