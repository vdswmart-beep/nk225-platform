# features/momentum/momentum_features.py — FIXED (BUG-03: "close" vs "Close")

import pandas as pd
from features.utils import melt_features


def compute_momentum_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les features de momentum sur 1M, 3M, 6M, 12M.

    Args:
        df: DataFrame avec colonnes ["ticker", "date", "close"] (normalisées en minuscule)
    """
    required = ["ticker", "date", "close"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans momentum_features: {missing}")

    df = df.sort_values(["ticker", "date"]).copy()

    windows = [21, 63, 126, 252]
    names   = ["mom_1m", "mom_3m", "mom_6m", "mom_12m"]

    for window, name in zip(windows, names):
        df[name] = df.groupby("ticker")["close"].pct_change(window)

    return melt_features(df, names)