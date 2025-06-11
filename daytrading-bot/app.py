import streamlit as st
import pandas as pd
from data_handler import fetch_data
from indicators import add_all_indicators
from strategy import recommend_trade
from visualize import plot_data as show_chart
import yfinance as yf
import matplotlib.pyplot as plt
import os
import csv
from datetime import datetime

st.set_page_config(page_title="Daytrading Bot", layout="wide")
st.title("📈 Daytrading Bot - Options Assistant")

# --- Tabs ---
tabs = st.tabs(["💡 Get Trade Idea", "📒 Trade Journal"])

with tabs[0]:
    st.header("Get Trade Recommendation")

    ticker = st.text_input("Enter Stock Ticker", value="AAPL").upper()
    timeframe = st.selectbox("Select Timeframe", ["4 Hours", "Weekly", "Monthly", "Yearly"])

    interval_map = {
        "4 Hours": ("4h", "5d"),
        "Weekly": ("1wk", "1y"),
        "Monthly": ("1mo", "5y"),
        "Yearly": ("1d", "1y")
    }

    if ticker and st.button("Analyze"):
        interval, period = interval_map[timeframe]

        try:
            ticker_data = yf.Ticker(ticker)
            expiry = ticker_data.options[0]
            stock_data, options_data = fetch_data(ticker, expiry, interval=interval, period=period)

            option_row = {
                'strike': options_data.iloc[0]['strike'],
                'impliedVolatility': options_data.iloc[0]['impliedVolatility'],
                'expiration': expiry
            }

            enriched_data = add_all_indicators(stock_data, option_row)
            trade_signals = recommend_trade(enriched_data, options_data, expiry)

            if isinstance(trade_signals, str):
                st.info(trade_signals)
            else:
                st.subheader("Top 3 Trade Candidates")
                trade_df = pd.DataFrame(trade_signals)

                # Display clean table with selected fields
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

                # Log top pick
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

            # Plot
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(enriched_data.index, enriched_data['Close'], label='Close')
            ax.plot(enriched_data.index, enriched_data['MA20'], label='MA20')
            ax.set_title(f"{ticker} Price and MA20")
            ax.legend()
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Error: {e}")

with tabs[1]:
    st.header("View Trade Journal")

    try:
        df = pd.read_csv("trade_log.csv", parse_dates=["Date"])

        tickers = df["Ticker"].unique().tolist()
        trade_types = df["Trade Type"].unique().tolist()

        col1, col2 = st.columns(2)
        with col1:
            selected_ticker = st.selectbox("Filter by Ticker", ["All"] + tickers)
        with col2:
            selected_type = st.selectbox("Filter by Trade Type", ["All"] + trade_types)

        start_date = st.date_input("Start Date", value=df["Date"].min().date())
        end_date = st.date_input("End Date", value=df["Date"].max().date())

        filtered = df.copy()
        if selected_ticker != "All":
            filtered = filtered[filtered["Ticker"] == selected_ticker]
        if selected_type != "All":
            filtered = filtered[filtered["Trade Type"] == selected_type]
        filtered = filtered[
            (filtered["Date"] >= pd.to_datetime(start_date)) &
            (filtered["Date"] <= pd.to_datetime(end_date))
        ]

        st.dataframe(filtered.sort_values(by="Date", ascending=False), use_container_width=True)

        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Filtered CSV", csv, "filtered_trades.csv", "text/csv")

    except FileNotFoundError:
        st.warning("No trade log file found.")
