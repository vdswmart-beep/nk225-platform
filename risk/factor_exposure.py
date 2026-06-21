import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def compute_beta(asset_returns, market_returns):
    model = LinearRegression()
    model.fit(market_returns.values.reshape(-1, 1), asset_returns.values)
    return model.coef_[0]


def portfolio_beta(returns_df, weights, market_returns):
    betas = []
    for col in returns_df.columns:
        beta = compute_beta(returns_df[col], market_returns)
        betas.append(beta)
    return np.dot(betas, weights)


def factor_exposure(returns_df, factor_df):
    exposures = {}
    for asset in returns_df.columns:
        model = LinearRegression()
        model.fit(factor_df, returns_df[asset])
        exposures[asset] = model.coef_
    return pd.DataFrame(exposures, index=factor_df.columns)


def sector_exposure(weights, sector_map):
    exposure = {}
    for asset, weight in weights.items():
        sector = sector_map.get(asset, "Unknown")
        exposure[sector] = exposure.get(sector, 0) + weight
    return exposure