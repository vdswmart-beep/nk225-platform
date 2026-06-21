# features/value/value_features.py — FIXED (BUG-12: melt_features importé, pas dupliqué)

import numpy as np
import pandas as pd
from features.utils import melt_features   # FIX BUG-12: import, ne pas redéfinir


def safe_col(df: pd.DataFrame, col: str) -> pd.Series:
    """Retourne la colonne convertie en float, ou NaN si absente."""
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce")
    return pd.Series(np.nan, index=df.index)


def compute_value_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    trailing_pe      = safe_col(df, "trailingPE")
    price_to_book    = safe_col(df, "priceToBook")
    enterprise_value = safe_col(df, "enterpriseValue")
    ebitda           = safe_col(df, "ebitda")
    free_cashflow    = safe_col(df, "freeCashflow")
    market_cap       = safe_col(df, "marketCap")

    df["pe"]             = trailing_pe
    df["pb"]             = price_to_book
    df["ev_ebitda"]      = enterprise_value / ebitda.replace(0, np.nan)
    df["earnings_yield"] = 1.0 / trailing_pe.replace(0, np.nan)
    df["fcf_yield"]      = free_cashflow / market_cap.replace(0, np.nan)

    return melt_features(df, ["pe", "pb", "ev_ebitda", "earnings_yield", "fcf_yield"])