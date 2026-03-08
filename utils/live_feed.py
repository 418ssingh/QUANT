import numpy as np


def simulate_live_feed(prices):
    live = []
    last = prices[-1]

    for _ in range(30):
        last *= (1 + np.random.normal(0, 0.002))
        live.append(last)

    return live
