import streamlit as st
import pandas as pd

def render_trade_journal():
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
