# features/technical/technical_features.py — FIXED (BUG-03: colonnes minuscules + guards high/low)

import pandas as pd
import numpy as np
from features.utils import melt_features


def compute_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule RSI(14), ATR(14), position dans les bandes de Bollinger(20).

    Args:
        df: DataFrame avec colonnes normalisées en minuscule.
            Colonnes requises : ticker, date, close.
            Colonnes optionnelles : high, low (nécessaires pour ATR).
    """
    required = ["ticker", "date", "close"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans technical_features: {missing}")

    has_hl = "high" in df.columns and "low" in df.columns

    df = df.sort_values(["ticker", "date"]).copy()

    # ── RSI(14) ───────────────────────────────────────────────────────
    delta    = df.groupby("ticker")["close"].diff()
    gain     = delta.clip(lower=0)
    loss     = (-delta).clip(lower=0)

    avg_gain = (
        gain.groupby(df["ticker"])
        .transform(lambda x: x.rolling(14, min_periods=14).mean())
    )
    avg_loss = (
        loss.groupby(df["ticker"])
        .transform(lambda x: x.rolling(14, min_periods=14).mean())
    )

    rs       = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi"] = 100 - (100 / (1 + rs))

    # ── ATR(14) ───────────────────────────────────────────────────────
    if has_hl:
        prev_close = df.groupby("ticker")["close"].shift(1)
        high_low   = df["high"] - df["low"]
        high_pc    = (df["high"] - prev_close).abs()
        low_pc     = (df["low"]  - prev_close).abs()
        tr         = pd.concat([high_low, high_pc, low_pc], axis=1).max(axis=1)
        df["atr"]  = (
            tr.groupby(df["ticker"])
            .transform(lambda x: x.rolling(14, min_periods=14).mean())
        )
    else:
        # Fallback : ATR approchée via la volatilité du close
        df["atr"] = (
            df.groupby("ticker")["close"]
            .transform(lambda x: x.rolling(14).std())
        )

    # ── Bollinger position ─────────────────────────────────────────────
    ma  = df.groupby("ticker")["close"].transform(lambda x: x.rolling(20).mean())
    std = df.groupby("ticker")["close"].transform(lambda x: x.rolling(20).std())
    upper = ma + 2 * std
    lower = ma - 2 * std
    denom = (upper - lower).replace(0, np.nan)
    df["bollinger_pos"] = (df["close"] - lower) / denom

    features = ["rsi", "atr", "bollinger_pos"]
    return melt_features(df, features)