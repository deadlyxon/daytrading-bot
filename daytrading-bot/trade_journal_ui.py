import streamlit as st
import pandas as pd

# Load trade log CSV
@st.cache_data
def load_trade_log(filename="trade_log.csv"):
    try:
        df = pd.read_csv(filename, parse_dates=["Date"])
        return df
    except FileNotFoundError:
        st.error("No trade_log.csv found.")
        return pd.DataFrame()

st.set_page_config(page_title="Trade Journal", layout="wide")
st.title("📒 Options Trade Journal")

df = load_trade_log()

if df.empty:
    st.stop()

# Sidebar Filters
st.sidebar.header("Filter Trades")
tickers = df["Ticker"].unique().tolist()
types = df["Trade Type"].unique().tolist()

selected_ticker = st.sidebar.selectbox("Ticker", ["All"] + tickers)
selected_type = st.sidebar.selectbox("Trade Type", ["All"] + types)
start_date = st.sidebar.date_input("Start Date", value=df["Date"].min().date())
end_date = st.sidebar.date_input("End Date", value=df["Date"].max().date())

# Apply filters
filtered = df.copy()
if selected_ticker != "All":
    filtered = filtered[filtered["Ticker"] == selected_ticker]
if selected_type != "All":
    filtered = filtered[filtered["Trade Type"] == selected_type]
filtered = filtered[
    (filtered["Date"] >= pd.to_datetime(start_date)) &
    (filtered["Date"] <= pd.to_datetime(end_date))
]

# Display
st.subheader("📈 Filtered Trade Log")
st.dataframe(filtered.sort_values(by="Date", ascending=False), use_container_width=True)

# Export
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download CSV", csv, "filtered_trades.csv", "text/csv")
