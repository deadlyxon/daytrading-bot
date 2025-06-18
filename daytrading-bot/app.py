import streamlit as st
import pandas as pd
from data_handler import fetch_data
from indicators import add_all_indicators, calculate_rsi, calculate_macd
from strategy import recommend_trade
import yfinance as yf
import matplotlib.pyplot as plt
import os
import csv
from datetime import datetime, time
from sklearn.linear_model import LinearRegression
import numpy as np
from visualize import plot_data

# Set Streamlit config first
st.set_page_config(page_title="Daytrading Bot", layout="wide")

# Check market open status
now = datetime.now().time()
market_open = time(8, 30)
market_close = time(15, 0)
if not (market_open <= now <= market_close):
    st.warning("⚠️ Market is closed. Data may be stale or incomplete.")

st.title("📈 Daytrading Bot - Options Assistant")

# --- Tabs ---
tabs = st.tabs(["💡 Get Trade Idea", "📒 Trade Journal", "ℹ️ Info"])

with tabs[0]:
    st.header("Get Trade Recommendation")

    ticker = st.text_input("Enter Stock Ticker", value="AAPL").upper()
    st.markdown("**Timeframe: 1 Week (Fixed)**")
    interval = "4h"
    period = "30d"  # Extended period to support longer MA

    option_type = st.radio("Option Type", ["Calls", "Puts"], horizontal=True)

    if ticker and st.button("Analyze"):
        try:
            def get_first_expiry(ticker):
                try:
                    return yf.Ticker(ticker).options[0]
                except Exception:
                    return None

            expiry = get_first_expiry(ticker)
            stock_data, calls, puts = fetch_data(ticker, expiry, interval=interval, period=period)
            options_data = calls if option_type == "Calls" else puts

            option_row = {
                'strike': options_data.iloc[0]['strike'],
                'impliedVolatility': options_data.iloc[0]['impliedVolatility'],
                'expiration': expiry
            }

            enriched_data = add_all_indicators(stock_data, option_row)
            enriched_data['RSI'] = calculate_rsi(enriched_data['Close'])
            enriched_data['MACD'], enriched_data['MACD_Signal'] = calculate_macd(enriched_data['Close'])

            trade_signals = recommend_trade(enriched_data, options_data, expiry)

            if isinstance(trade_signals, str):
                st.info(trade_signals)
            else:
                st.subheader("Top 3 Trade Candidates")
                trade_df = pd.DataFrame(trade_signals)

                display_df = trade_df[[
                    'contractSymbol', 'type', 'strike', 'lastPrice', 'bid', 'ask',
                    'volume', 'openInterest', 'impliedVolatility',
                    'Delta', 'Gamma', 'Theta', 'IV_Rank', 'Moneyness'
                ]].copy()

                display_df.columns = [
                    'Contract', 'Type', 'Strike', 'Last Price', 'Bid', 'Ask',
                    'Volume', 'Open Interest', 'IV',
                    'Delta', 'Gamma', 'Theta', 'IV Rank', 'Moneyness'
                ]

                st.dataframe(display_df.style.format({
                    'Strike': "{:.2f}",
                    'Last Price': "{:.2f}",
                    'Bid': "{:.2f}",
                    'Ask': "{:.2f}",
                    'IV': "{:.2%}",
                    'Delta': "{:.2f}",
                    'Gamma': "{:.2f}",
                    'Theta': "{:.2f}",
                    'IV Rank': "{:.2%}",
                    'Moneyness': "{:.2%}"
                }), use_container_width=True)

                top_pick = trade_signals[0]
                with open("trade_log.csv", mode='a', newline='') as file:
                    writer = csv.writer(file)
                    if os.path.getsize("trade_log.csv") == 0:
                        writer.writerow(["Date", "Ticker", "Expiry", "Trade Type", "Strike", "IV"])
                    writer.writerow([
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ticker,
                        expiry,
                        top_pick.get("type", "N/A"),
                        top_pick.get("strike", "N/A"),
                        top_pick.get("impliedVolatility", "N/A")
                    ])

            # --- Create prediction data ---
            N_PREDICT = 5
            df = enriched_data[['Close']].dropna().copy()
            df = df.reset_index(names='Datetime')
            df['TimeIndex'] = np.arange(len(df))
            X = df[['TimeIndex']]
            y = df['Close']
            model = LinearRegression().fit(X, y)
            future_indexes = np.arange(len(df), len(df) + N_PREDICT).reshape(-1, 1)
            future_preds = model.predict(future_indexes)
            last_timestamp = df['Datetime'].iloc[-1]
            freq = df['Datetime'].diff().median()
            future_dates = [last_timestamp + freq * (i + 1) for i in range(N_PREDICT)]

            # Build prediction DataFrame
            prediction_df = pd.DataFrame({'Predicted Close': future_preds}, index=pd.to_datetime(future_dates))

            # --- Display full chart with prediction ---
            plot_data(enriched_data, prediction_df)



        except Exception as e:
            st.error(f"Error: {e}")

with tabs[1]:
    from trade_journal_ui import render_trade_journal
    render_trade_journal()

with tabs[2]:
    st.header("ℹ️ Indicator Reference Guide")

    st.markdown("""
    ### 📘 Definitions

    **MA20**: 20-period Moving Average — smooths price action.

    **RSI**: Relative Strength Index. Below 30 = oversold, Above 70 = overbought.

    **MACD**: Shows trend momentum.

    **Z-Score**: Distance from price to recent mean, measured in standard deviations.

    **Moneyness**: Difference between strike and price as % of price.

    **Implied Volatility (IV)**: Option's expected volatility.

    **IV Rank**: Position of current IV in its 1-year range.

    **Delta**: Sensitivity of option price to stock price.

    **Gamma**: Sensitivity of delta to price changes.

    **Theta**: Option value decay over time.

    **Filters**:
    - Volume > 500
    - Open Interest > 500
    - IV Rank ≤ 75%
    - Delta between 0.25–0.7
    - Moneyness within ±10%
    - Bid/Ask spread ≤ 20%
    """)
