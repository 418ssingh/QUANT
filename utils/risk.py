import numpy as np


def atr_position_sizing(df, capital, risk_pct=0.02):

    atr = (df["High"] - df["Low"]).rolling(14).mean().iloc[-1]
    atr = atr.item()

    close_price = df["Close"].iloc[-1].item()

    risk_amount = capital * risk_pct
    shares = risk_amount / atr

    position_value = shares * close_price

    return float(position_value)


def kelly_position_sizing(df, capital):

    wins = df[df["Strategy_Return"] > 0]["Strategy_Return"]
    losses = df[df["Strategy_Return"] < 0]["Strategy_Return"]

    if len(wins) == 0 or len(losses) == 0:
        return 0.1 * capital

    win_rate = len(wins) / len(df)

    avg_win = wins.mean().item()
    avg_loss = abs(losses.mean()).item()

    if avg_loss == 0:
        return 0.1 * capital

    wl_ratio = avg_win / avg_loss

    kelly_fraction = win_rate - (1 - win_rate) / wl_ratio

    return float(max(kelly_fraction, 0) * capital)


def monte_carlo_simulation(df, paths=50, days=60):

    returns = df["Strategy_Return"].dropna()

    sims = np.zeros((days, paths))

    for p in range(paths):
        value = 1
        for d in range(days):
            value *= (1 + np.random.choice(returns))
            sims[d, p] = value

    return sims
