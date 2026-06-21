# math_engine/statistical_models.py

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy import stats
import warnings
warnings.filterwarnings("ignore")


def ols_factor_regression(returns: pd.Series, factors: pd.DataFrame) -> dict:
    """OLS regression of asset returns on factor returns."""
    aligned = factors.align(returns, join="inner")
    X, y = aligned[0].dropna(), aligned[1].dropna()
    idx = X.index.intersection(y.index)
    X, y = X.loc[idx], y.loc[idx]

    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    residuals = y - y_pred

    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y - y.mean())**2)
    r2 = 1 - ss_res/ss_tot if ss_tot > 0 else 0

    n, k = len(y), X.shape[1]
    se = np.sqrt(ss_res / (n - k - 1) * np.linalg.pinv(X.T @ X).diagonal()) if n > k+1 else np.zeros(k)
    t_stats = model.coef_ / (se + 1e-10)
    p_values = [2 * (1 - stats.t.cdf(abs(t), df=n-k-1)) for t in t_stats]

    return {
        "betas":    dict(zip(X.columns, model.coef_)),
        "alpha":    float(model.intercept_),
        "r_squared": float(r2),
        "t_stats":  dict(zip(X.columns, t_stats)),
        "p_values": dict(zip(X.columns, p_values)),
        "residuals": residuals,
        "n_obs":    n,
    }


def pca_analysis(returns: pd.DataFrame, n_components: int = 5) -> dict:
    """PCA decomposition of return covariance."""
    clean = returns.dropna()
    scaler = StandardScaler()
    scaled = scaler.fit_transform(clean)

    n_comp = min(n_components, clean.shape[1], clean.shape[0]-1)
    pca = PCA(n_components=n_comp)
    pca.fit(scaled)

    loadings = pd.DataFrame(
        pca.components_.T,
        index=clean.columns,
        columns=[f"PC{i+1}" for i in range(n_comp)],
    )
    explained = pca.explained_variance_ratio_

    scores = pd.DataFrame(
        pca.transform(scaled),
        index=clean.index,
        columns=[f"PC{i+1}" for i in range(n_comp)],
    )

    return {
        "explained_variance": explained.tolist(),
        "cumulative_variance": np.cumsum(explained).tolist(),
        "loadings":  loadings,
        "scores":    scores,
        "n_components": n_comp,
    }


def rolling_factor_exposure(returns: pd.Series, benchmark: pd.Series,
                             window: int = 63) -> pd.DataFrame:
    """Rolling OLS beta and alpha vs a benchmark."""
    aligned = returns.align(benchmark, join="inner")
    r, b = aligned[0].dropna(), aligned[1].dropna()
    idx = r.index.intersection(b.index)
    r, b = r.loc[idx], b.loc[idx]

    rows = []
    for i in range(window, len(r)+1):
        y  = r.iloc[i-window:i].values
        x  = b.iloc[i-window:i].values.reshape(-1,1)
        m  = LinearRegression().fit(x, y)
        rows.append({"date": r.index[i-1], "beta": m.coef_[0], "alpha": m.intercept_})

    return pd.DataFrame(rows).set_index("date")


def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    return returns.corr()


def rolling_correlation(s1: pd.Series, s2: pd.Series, window: int = 63) -> pd.Series:
    return s1.rolling(window).corr(s2)
