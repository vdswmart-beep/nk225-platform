import pandas as pd

from features.value.value_features import compute_value_features
from features.quality.quality_features import compute_quality_features
from features.growth.growth_features import compute_growth_features
from features.momentum.momentum_features import compute_momentum_features
from features.volatility.volatility_features import compute_volatility_features
from features.technical.technical_features import compute_technical_features


def build_feature_matrix(prices_df, fundamentals_df):
    """
    Build complete factor matrix.

    Parameters
    ----------
    prices_df : DataFrame
        Historical prices.

    fundamentals_df : DataFrame
        Fundamental snapshot by ticker.

    Returns
    -------
    DataFrame
        date | ticker | feature | value
    """

    prices_df = prices_df.copy()
    fundamentals_df = fundamentals_df.copy()

    # ----------------------------------
    # PRICE DATA NORMALIZATION
    # ----------------------------------

    if isinstance(prices_df.index, pd.MultiIndex):
        prices_df = prices_df.reset_index()

    elif "date" not in prices_df.columns:
        prices_df = prices_df.reset_index()

    # ----------------------------------
    # FUNDAMENTAL DATA NORMALIZATION
    # ----------------------------------

    if "ticker" not in fundamentals_df.columns:

        fundamentals_df = fundamentals_df.reset_index()

        if "index" in fundamentals_df.columns:
            fundamentals_df = fundamentals_df.rename(
                columns={"index": "ticker"}
            )

    # ----------------------------------
    # MERGE
    # ----------------------------------

    df = prices_df.merge(
        fundamentals_df,
        on="ticker",
        how="left"
    )

    print("\nMERGED DF")
    print(df.head())
    print("\nMERGED COLUMNS")
    print(sorted(df.columns.tolist()))
    # -------------------------------
    # PRICE COLUMN NORMALIZATION
    # -------------------------------
    
    price_rename = {
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    }
    
    df = df.rename(columns=price_rename)
    
    if "close" in df.columns:
        df["price"] = df["close"]
    
    elif "regularMarketPrice" in df.columns:
        df["price"] = df["regularMarketPrice"]
        df["close"] = df["regularMarketPrice"]
    
    rename_map = {
        "marketCap": "market_cap",
        "bookValue": "book_value_per_share",
        "totalDebt": "debt",
        "totalCash": "cash",
        "ebitda": "ebitda",
        "freeCashflow": "fcf",
    }
    
    df = df.rename(columns=rename_map)

    feature_dfs = []

    # Value
    feature_dfs.append(compute_value_features(df))

    # Quality
    feature_dfs.append(compute_quality_features(df))

    # Growth
    feature_dfs.append(compute_growth_features(df))

    # Momentum
    feature_dfs.append(compute_momentum_features(df))

    # Volatility
    feature_dfs.append(compute_volatility_features(df))

    # Technical
    feature_dfs.append(compute_technical_features(df))

    features = pd.concat(
        feature_dfs,
        axis=0,
        ignore_index=True
    )

    features["value"] = pd.to_numeric(
        features["value"],
        errors="coerce"
    )

    features = features.replace(
        [float("inf"), -float("inf")],
        pd.NA
    )

    features = features.dropna(subset=["value"])

    return features
    print("\nMERGED DF COLUMNS")
    print(sorted(df.columns.tolist()))