import numpy as np


# ============================
# BACKTEST PERFORMANCE ENGINE
# ============================
def run_backtest(df):
    returns = df["Strategy_Return"].dropna()

    total_return = returns.sum() * 100

    # ✅ Sharpe Safe Handling
    if returns.std() == 0 or returns.std() is None:
        sharpe = 0
    else:
        sharpe = returns.mean() / returns.std()

    # Drawdown Calculation
    cumulative = (1 + returns).cumprod()
    peak = cumulative.cummax()
    drawdown = ((cumulative - peak) / peak).min() * 100

    return {
        "total_return": total_return,
        "sharpe": sharpe,
        "drawdown": drawdown
    }
