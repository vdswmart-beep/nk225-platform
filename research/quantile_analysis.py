import pandas as pd
import numpy as np

class QuantileAnalysis:

    @staticmethod
    def compute_quantiles(factor, n_quantiles=5):
        return pd.qcut(factor, n_quantiles, labels=False)

    @staticmethod
    def quantile_returns(factor, returns, n_quantiles=5):
        q = QuantileAnalysis.compute_quantiles(factor, n_quantiles)

        df = pd.DataFrame({
            "factor": factor,
            "returns": returns,
            "quantile": q
        })

        return df.groupby("quantile")["returns"].mean()

    @staticmethod
    def quantile_spread(quantile_returns):
        return quantile_returns.iloc[-1] - quantile_returns.iloc[0]