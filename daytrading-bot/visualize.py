import matplotlib.pyplot as plt
import streamlit as st

def plot_data(df, prediction_df=None):
    """
    Plots historical stock data and optionally overlays a prediction series.

    Parameters:
    - df: DataFrame with columns like 'Close', 'MA20', and datetime index
    - prediction_df: Optional DataFrame with predicted values and datetime index
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    if 'Close' in df.columns:
        ax.plot(df.index, df['Close'], label='Close Price')

    if 'MA20' in df.columns and df['MA20'].notna().sum() > 1:
        ax.plot(df.index, df['MA20'], label='MA20', linestyle='--')

    if prediction_df is not None:
        ax.plot(prediction_df.index, prediction_df['Predicted Close'], label='Prediction', linestyle=':', color='green')

    ax.set_title("Stock Price with Indicators and Prediction")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    st.pyplot(fig)
