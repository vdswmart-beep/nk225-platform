import pandas as pd
import numpy as np


def melt_features(df, feature_cols):
    """
    Transforme un DataFrame wide en format long standard:
    date | ticker | feature | value
    """
    return df.melt(
        id_vars=["date", "ticker"],
        value_vars=feature_cols,
        var_name="feature",
        value_name="value"
    )


def safe_divide(numerator, denominator):
    """
    Division robuste qui évite inf / NaN explosifs
    """
    result = numerator / denominator
    result = result.replace([np.inf, -np.inf], np.nan)
    return result


def winsorize(series, lower=0.01, upper=0.99):
    """
    Coupe les extrêmes (utile pour facteurs quant)
    """
    return series.clip(
        lower=series.quantile(lower),
        upper=series.quantile(upper)
    )