import numpy as np
import pandas as pd

class ICAnalysis:

    @staticmethod
    def compute_ic(factor, returns):
        return factor.corr(returns, method='spearman')

    @staticmethod
    def compute_ic_series(factor_df, returns_df):
        ic_series = factor_df.corrwith(returns_df, axis=1, method='spearman')
        return ic_series

    @staticmethod
    def ic_metrics(ic_series):
        ic_mean = ic_series.mean()
        ic_std = ic_series.std()
        icir = ic_mean / ic_std if ic_std != 0 else 0

        hit_ratio = (ic_series > 0).mean()

        return {
            "ic_mean": ic_mean,
            "ic_std": ic_std,
            "icir": icir,
            "hit_ratio": hit_ratio
        }