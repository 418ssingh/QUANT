import numpy as np


def moving_average_crossover(df):
    df = df.copy()

    df["SMA10"] = df["Close"].rolling(10).mean()
    df["SMA30"] = df["Close"].rolling(30).mean()

    df["Signal"] = 0
    df.loc[df["SMA10"] > df["SMA30"], "Signal"] = 1
    df.loc[df["SMA10"] < df["SMA30"], "Signal"] = -1

    df["Return"] = df["Close"].pct_change()
    df["Strategy_Return"] = df["Return"] * df["Signal"].shift(1)

    return df


def rsi_strategy(df, period=14):
    df = df.copy()

    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df["Signal"] = 0
    df.loc[df["RSI"] < 30, "Signal"] = 1
    df.loc[df["RSI"] > 70, "Signal"] = -1

    df["Return"] = df["Close"].pct_change()
    df["Strategy_Return"] = df["Return"] * df["Signal"].shift(1)

    return df
