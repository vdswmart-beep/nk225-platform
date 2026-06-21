# risk/var.py — FIXED (BUG-08: empty tail guard returns 0.0 instead of nan)

import numpy as np


def historical_var(returns, confidence=0.95):
    arr = np.sort(np.asarray(returns, dtype=float))
    idx = int((1 - confidence) * len(arr))
    if idx < 1:
        return 0.0
    return abs(arr[idx])


def historical_cvar(returns, confidence=0.95):
    arr = np.sort(np.asarray(returns, dtype=float))
    idx = int((1 - confidence) * len(arr))
    tail = arr[:idx]
    if len(tail) == 0:
        return 0.0
    return abs(np.mean(tail))


def portfolio_var(returns_df, weights, confidence=0.95):
    portfolio_returns = returns_df @ weights
    return historical_var(portfolio_returns, confidence)


def portfolio_cvar(returns_df, weights, confidence=0.95):
    portfolio_returns = returns_df @ weights
    return historical_cvar(portfolio_returns, confidence)
