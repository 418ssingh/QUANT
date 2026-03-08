import pandas as pd
import yfinance as yf


# ============================
# LIVE P&L TRACKER
# ============================
def calculate_live_pnl(symbol, capital, entry_price):
    # Fetch Live Price
    price = yf.Ticker(symbol).history(period="1d")["Close"].iloc[-1]

    # Quantity Purchased
    qty = capital // price

    # Live Profit/Loss
    pnl = (price - entry_price) * qty

    return pd.DataFrame({
        "Symbol": [symbol],
        "Entry Price": [entry_price],
        "Live Price": [price],
        "Quantity": [qty],
        "Live P&L": [pnl]
    })
