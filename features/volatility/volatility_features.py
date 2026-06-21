# features/volatility/volatility_features.py — FIXED (BUG-03: "close" vs "Close")

import pandas as pd
import numpy as np
from features.utils import melt_features


def compute_volatility_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule la volatilité réalisée sur 20j, 63j, 252j.

    Args:
        df: DataFrame avec colonnes normalisées en minuscule.
    """
    required = ["ticker", "date", "close"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans volatility_features: {missing}")

    df = df.sort_values(["ticker", "date"]).copy()

    returns = df.groupby("ticker")["close"].pct_change()

    for window, name in zip([20, 63, 252], ["vol_20d", "vol_63d", "vol_252d"]):
        df[name] = (
            returns
            .groupby(df["ticker"])
            .transform(lambda x: x.rolling(window).std())
        )

    return melt_features(df, ["vol_20d", "vol_63d", "vol_252d"])