import pandas as pd

class RegimeAnalysis:

    @staticmethod
    def split_regimes(data, n_regimes=3):
        return pd.qcut(data.index, n_regimes, labels=False)

    @staticmethod
    def regime_ic(ic_series, regimes):
        df = pd.DataFrame({
            "ic": ic_series,
            "regime": regimes
        })

        return df.groupby("regime")["ic"].mean()

    @staticmethod
    def stability_score(regime_ic):
        return regime_ic.std()