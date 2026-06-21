# pipelines/research_pipeline.py

import logging
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from research.ic_analysis import ICAnalysis
from research.statistical_tests import StatisticalTests
from research.quantile_analysis import QuantileAnalysis
from research.regime_analysis import RegimeAnalysis
from research.capacity_analysis import CapacityAnalysis

logger = logging.getLogger("ResearchPipeline")


@dataclass
class ResearchOutputs:
    ic_series:   pd.Series  = field(default_factory=pd.Series)
    ic_stats:    dict       = field(default_factory=dict)
    factor_stats:dict       = field(default_factory=dict)
    valid_factors:list      = field(default_factory=list)


class ResearchPipeline:

    def run(self, features_long: pd.DataFrame, returns: pd.DataFrame) -> ResearchOutputs:
        logger.info("Running research pipeline...")
        results = ResearchOutputs()

        try:
            features_pivot = features_long.pivot_table(
                index=["date","ticker"], columns="feature", values="value"
            )
            ret_aligned = returns.stack().rename("returns")
            ret_aligned.index.names = ["date","ticker"]

            factor_stats = {}
            valid_factors = []

            for factor_name in features_pivot.columns:
                try:
                    factor_series = features_pivot[factor_name].dropna()
                    if len(factor_series) < 30:
                        continue
                    factor_wide = factor_series.unstack("ticker")
                    returns_wide = returns.reindex(factor_wide.index)
                    ic_s = ICAnalysis.compute_ic_series(factor_wide, returns_wide)
                    stats = ICAnalysis.ic_metrics(ic_s.dropna())
                    t_stat = StatisticalTests.t_test(ic_s.dropna())
                    stats.update(t_stat)
                    factor_stats[factor_name] = stats
                    if stats["ic_mean"] > 0.02 and stats.get("p_value", 1) < 0.1:
                        valid_factors.append(factor_name)
                except Exception as e:
                    logger.debug(f"Factor {factor_name} failed: {e}")

            results.factor_stats  = factor_stats
            results.valid_factors = valid_factors
            logger.info(f"Valid factors: {valid_factors}")

        except Exception as e:
            logger.error(f"Research pipeline failed: {e}")

        return results
