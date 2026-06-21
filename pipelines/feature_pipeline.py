# pipelines/feature_pipeline.py

import logging
import pandas as pd
from dataclasses import dataclass, field
from features.build_features import build_feature_matrix

logger = logging.getLogger("FeaturePipeline")


@dataclass
class FeatureOutputs:
    features_long:  pd.DataFrame = field(default_factory=pd.DataFrame)
    features_wide:  pd.DataFrame = field(default_factory=pd.DataFrame)


class FeaturePipeline:

    def run(self, prices: pd.DataFrame, fundamentals: pd.DataFrame) -> FeatureOutputs:
        logger.info("Building feature matrix...")

        features_long = build_feature_matrix(prices, fundamentals)
        logger.info(f"Features (long): {features_long.shape}")

        features_wide = (
            features_long
            .pivot_table(index=["date", "ticker"], columns="feature", values="value")
            .reset_index()
        )
        features_wide.columns.name = None
        logger.info(f"Features (wide): {features_wide.shape}")

        return FeatureOutputs(features_long=features_long, features_wide=features_wide)
