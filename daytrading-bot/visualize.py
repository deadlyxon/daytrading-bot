import matplotlib.pyplot as plt
import seaborn as sns

def plot_data(df):
    plt.figure(figsize=(10, 5))
    sns.lineplot(x=df.index, y=df['Close'], label="Close Price")
    sns.lineplot(x=df.index, y=df['MA20'], label="20-day MA")
    plt.title("Stock Price with Moving Average")
    plt.legend()
    plt.show()
