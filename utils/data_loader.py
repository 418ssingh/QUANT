import yfinance as yf


def load_market_data(symbol):
    df = yf.download(symbol, period="6mo", interval="1d")
    df.dropna(inplace=True)
    return df
