# features/growth/growth_features.py — FIXED: null guards

import numpy as np
from features.utils import melt_features


def safe_col(df, col):
    if col in df.columns:
        import pandas as pd
        return pd.to_numeric(df[col], errors="coerce")
    return np.full(len(df), np.nan)


def compute_growth_features(df):
    df = df.copy()
    df["revenue_growth"]  = safe_col(df, "revenueGrowth")
    df["earnings_growth"] = safe_col(df, "earningsGrowth")
    fwd = safe_col(df, "forwardEps")
    trl = safe_col(df, "trailingEps")
    df["eps_revision"] = fwd - trl
    return melt_features(df, ["revenue_growth", "earnings_growth", "eps_revision"])
