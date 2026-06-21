# features/quality/quality_features.py — FIXED (BUG-08: null guards on all columns)

import numpy as np
from features.utils import melt_features


def safe_col(df, col):
    if col in df.columns:
        import pandas as pd
        return pd.to_numeric(df[col], errors="coerce")
    return np.full(len(df), np.nan)


def compute_quality_features(df):
    df = df.copy()
    df["roe"]              = safe_col(df, "returnOnEquity")
    df["roa"]              = safe_col(df, "returnOnAssets")
    df["gross_margin"]     = safe_col(df, "grossMargins")
    df["operating_margin"] = safe_col(df, "operatingMargins")
    return melt_features(df, ["roe", "roa", "gross_margin", "operating_margin"])
