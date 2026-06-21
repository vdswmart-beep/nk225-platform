import numpy as np

def compute_drawdown(prices):
    cumulative_max = prices.cummax()
    drawdown = (prices - cumulative_max) / cumulative_max
    return drawdown


def max_drawdown(prices):
    dd = compute_drawdown(prices)
    return dd.min()


def drawdown_duration(prices):
    dd = compute_drawdown(prices)
    duration = (dd < 0).astype(int)
    return duration.groupby((duration == 0).cumsum()).cumsum().max()