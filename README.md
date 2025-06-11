# daytrading-bot
# 📈 Daytrading Bot

An intelligent options trading assistant that analyzes stock data, scans option chains, calculates advanced indicators (IV Rank, Greeks, Moneyness), and recommends top trades based on technical filters.

Built with:
- Python (Pandas, NumPy, SciPy, Matplotlib)
- Streamlit (UI)
- yFinance (Market Data)

---

## 🚀 Features

✅ User inputs stock ticker  
✅ Selectable chart timeframes (4H, Weekly, Monthly, Yearly)  
✅ Automatic calculation of:
- 5/10/20-day moving averages
- Bollinger Bands
- Z-Score
- Historical Volatility
- Moneyness
- IV Rank
- Option Greeks (Delta, Gamma, Theta)

✅ Filters out bad contracts with:
- Tight bid/ask spread  
- High volume + open interest  
- Favorable Delta range (0.25–0.70)  
- Reasonable IV Rank (< 75%)  
- Near-the-money contracts only  

✅ Trade Journal with exportable CSV log  
✅ Top 3 trade ideas displayed per signal

---

## 🖥 How to Run Locally

```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/daytrading-bot.git
cd daytrading-bot

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
