# research/factor_validation.py — FIXED (BUG-02: @staticmethod + absolute imports)

from research.ic_analysis import ICAnalysis
from research.quantile_analysis import QuantileAnalysis
from research.statistical_tests import StatisticalTests


class FactorValidation:

    @staticmethod   # FIX: was missing — caused TypeError on any instance/class call
    def validate(factor_df, returns_df):
        ic_series = ICAnalysis.compute_ic_series(factor_df, returns_df)
        ic_stats  = ICAnalysis.ic_metrics(ic_series)

        t_test  = StatisticalTests.t_test(ic_series)
        jb_test = StatisticalTests.jarque_bera(ic_series)

        quantile_ret = QuantileAnalysis.quantile_returns(
            factor_df.stack(), returns_df.stack()
        )
        spread = QuantileAnalysis.quantile_spread(quantile_ret)

        confidence_score = (
            ic_stats["icir"] * 0.4
            + spread * 0.3
            + ic_stats["hit_ratio"] * 0.3
        )

        valid_factor = (
            ic_stats["ic_mean"] > 0
            and t_test["p_value"] < 0.05
            and spread > 0
        )

        return {
            "valid_factor": valid_factor,
            "confidence_score": confidence_score,
            "statistics": {
                "ic": ic_stats,
                "t_test": t_test,
                "jarque_bera": jb_test,
                "quantile_spread": spread,
            },
        }
