# math_engine/hypothesis_testing.py

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import adfuller, coint
import warnings
warnings.filterwarnings("ignore")


def adf_test(series: pd.Series) -> dict:
    """Augmented Dickey-Fuller unit root test."""
    clean = series.dropna()
    result = adfuller(clean, autolag="AIC")
    return {
        "adf_stat":    float(result[0]),
        "p_value":     float(result[1]),
        "n_lags":      int(result[2]),
        "n_obs":       int(result[3]),
        "critical_1%": float(result[4]["1%"]),
        "critical_5%": float(result[4]["5%"]),
        "is_stationary": result[1] < 0.05,
    }


def jarque_bera_test(series: pd.Series) -> dict:
    clean = series.dropna()
    stat, p = stats.jarque_bera(clean)
    return {
        "jb_stat":    float(stat),
        "p_value":    float(p),
        "skewness":   float(clean.skew()),
        "kurtosis":   float(clean.kurtosis()),
        "is_normal":  p > 0.05,
    }


def t_test_mean(series: pd.Series, mu0: float = 0.0) -> dict:
    clean = series.dropna()
    t, p = stats.ttest_1samp(clean, mu0)
    return {
        "t_stat":    float(t),
        "p_value":   float(p),
        "mean":      float(clean.mean()),
        "std":       float(clean.std()),
        "n_obs":     len(clean),
        "significant": p < 0.05,
    }


def cointegration_test(s1: pd.Series, s2: pd.Series) -> dict:
    """Engle-Granger cointegration test for pairs trading."""
    aligned = s1.align(s2, join="inner")
    a, b = aligned[0].dropna(), aligned[1].dropna()
    idx = a.index.intersection(b.index)
    a, b = a.loc[idx], b.loc[idx]
    score, pvalue, crits = coint(a, b)
    return {
        "coint_stat":  float(score),
        "p_value":     float(pvalue),
        "critical_5%": float(crits[1]),
        "is_cointegrated": pvalue < 0.05,
    }


def bootstrap_ci(series: pd.Series, stat_fn=np.mean,
                 n_bootstrap: int = 1000, ci: float = 0.95) -> dict:
    clean = series.dropna().values
    boot_stats = [stat_fn(np.random.choice(clean, len(clean), replace=True))
                  for _ in range(n_bootstrap)]
    alpha = 1 - ci
    lo = np.percentile(boot_stats, alpha/2 * 100)
    hi = np.percentile(boot_stats, (1 - alpha/2) * 100)
    return {
        "point_estimate": float(stat_fn(clean)),
        "ci_lower":       float(lo),
        "ci_upper":       float(hi),
        "std_error":      float(np.std(boot_stats)),
        "n_bootstrap":    n_bootstrap,
    }


def run_all_tests(series: pd.Series) -> dict:
    return {
        "adf":         adf_test(series),
        "jarque_bera": jarque_bera_test(series),
        "t_test":      t_test_mean(series),
        "bootstrap":   bootstrap_ci(series),
    }
